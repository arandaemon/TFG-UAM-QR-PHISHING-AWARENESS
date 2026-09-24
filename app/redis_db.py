import os
import redis
import hashlib
import secrets
from flask import session
from flask_limiter import Limiter
import time

# Mitigación de CWE-312
# Al usar redis, los datos sensibles (email, centro, tokens) no se envían
# al navegador en la cookie, evitando su exposición en el lado del cliente.
# Configuramos la conexión a Redis gracias al DNS interno de Docker Compose
conexion_redis = redis.from_url('redis://redis:6379')


# No rechazamos en duro en el momento del envío. Grabamos TODO
# con sus señales y contamos SOLO lo limpio. Marcar != bloquear, así que
# podemos ser sensibles con el tiempo humano sin perder usuarios reales:
# el dudoso queda grabado y, si era humano, cuenta igual.

# Umbral de "tiempo humano" nadie lee la página y envía en menos de N segundos.
# Al ser una señal (no un bloqueo) podemos subirlo sin castigar a nadie real.
UMBRAL_TIEMPO_HUMANO = float(os.environ.get("UMBRAL_TIEMPO_HUMANO", "1.0"))

# Señal de velocidad de correos NUEVOS por IP. Desactivada por defecto para
# no penalizar el NAT de Eduroam mientras no se calibre con logs reales.
# Se activa poniendo IP_SIGNAL_ACTIVA=true en el .env.
IP_SIGNAL_ACTIVA = os.environ.get("IP_SIGNAL_ACTIVA", "false").lower() == "true"
IP_VENTANA_SEG = int(os.environ.get("IP_VENTANA_SEG", "3600"))      # Ventana deslizante (1h por defecto)
IP_UMBRAL_CORREOS = int(os.environ.get("IP_UMBRAL_CORREOS", "20"))  # Correos distintos/ventana que disparan la señal

# Función para identificar a cada usuario individualmente, saltándonos el NAT
def obtener_id_sesion():
    if 'limiter_id' not in session:
        # Si el usuario es nuevo, le damos un ID aleatorio temporal
        session['limiter_id'] = secrets.token_hex(8)
    return session['limiter_id']

# Inicializamos el limitador
# He decidido limitar por token y no por IP
# Ya que si las peticiones viene de Eduroam
# Usaran la misma IP
# Limitaré asimetricamente yo el endpoint crítico /validar
limiter = Limiter(
    key_func=obtener_id_sesion,
    storage_uri="redis://redis:6379",
    strategy="fixed-window"
)

# Convierte el email a un hash
def convertir_email_hash(email):
    secret_salt = os.environ.get("SECRET_SALT")
    email_limpio = email.lower().strip()
    datos_a_hashear = f"{secret_salt}{email_limpio}".encode('utf-8')
    email_hash = hashlib.sha256(datos_a_hashear).hexdigest()
    return email_hash

def detector_de_fases(fase, centro="desconocido"):
    ''' Embudo de EXPOSICIÓN (visitas), dedup por sesión.
        Fases visita: '1_qr' (escaneo) y '2_email' (llega al formulario).
        Estas fases miden cuánta gente se expone/engancha, y por definición
        son eventos de visita: una visita es una visita. El IMPACTO real
        (fase '3_password' = víctima única) se cuenta aparte, por hash de
        email y solo si NO es sospechoso (ver registrar_impacto_limpio).
    '''
    # Extraemos el identificador de sesión que creamos en la ruta principal
    visitor_id = session.get('visitor_id')
    if not visitor_id:
        visitor_id = session.get('limiter_id') # Fallback de seguridad

    # PROTECCIÓN: Si el usuario accedió directamente saltándose el código QR
    if not visitor_id:
        visitor_id = secrets.token_hex(16)
        session['visitor_id'] = visitor_id

    timestamp_actual = int(time.time())

    # Usamos Sets (conjuntos) ya que si el valor ya esta en el conjunto no
    # Sumará 1, devolverá 0
    es_nuevo_global = conexion_redis.sadd(f"visitantes_unicos_fase:{fase}", visitor_id)
    if es_nuevo_global == 1:
        conexion_redis.hincrby("embudo:fase", fase, 1) # Embudo global de toda la UAM
        # Impacto a la línea temporal global
        # {miembro: puntuacion} en nuestro caso la puntuación será
        # el timestamp actual, asi se ordena el conjunto
        conexion_redis.zadd(f"timeline:global:{fase}", {visitor_id: timestamp_actual})

    if centro and centro != "desconocido":
        es_nuevo_fac = conexion_redis.sadd(f"visitantes_unicos_facultad:{centro}:{fase}", visitor_id)
        if es_nuevo_fac == 1:
            conexion_redis.hincrby(f"embudo_facultad:{centro}", fase, 1) # Embudo específico
            conexion_redis.zadd(f"timeline:{centro}:{fase}", {visitor_id: timestamp_actual})

# Con ~4 correos distintos por IP al día en tráfico legítimo, un pico de
# decenas de correos distintos desde una IP en una hora canta. Esto NO
# bloquea (para no castigar al NAT): solo aporta una señal de sospecha más.

def senal_velocidad_ip(ip, email_hash):
    if not IP_SIGNAL_ACTIVA or not ip or not email_hash:
        return False
    clave = f"ip:emails:{ip}"
    ahora = int(time.time())
    # ZSET email_hash -> timestamp; ventana deslizante de IP_VENTANA_SEG
    conexion_redis.zadd(clave, {email_hash: ahora})
    conexion_redis.zremrangebyscore(clave, "-inf", ahora - IP_VENTANA_SEG)
    conexion_redis.expire(clave, IP_VENTANA_SEG)
    correos_distintos = conexion_redis.zcard(clave)
    return correos_distintos > IP_UMBRAL_CORREOS


# Cada POST a /validar deja rastro aquí, sea limpio o sospechoso. Esto es lo
# que permite el "punto dulce": el usuario dudoso ya no se pierde (queda
# grabado y, si era humano, cuenta), y "N envíos apartados" pasa a ser un
# resultado presentable para la memoria. Mantenemos además contadores
# agregados para que el panel se lea en O(1).

def registrar_evento_cuarentena(email_hash, centro, ubicacion, ip, sospechoso, senales):
    conexion_redis.xadd("cuarentena:eventos", {
        "email_hash": email_hash or "",
        "centro": centro or "desconocido",
        "ubicacion": ubicacion or "desconocida",
        "ip": ip or "",
        "sospechoso": "1" if sospechoso else "0",
        "senales": ",".join(senales) if senales else "",
        "ts": int(time.time()),
    })

    # Contadores agregados para lectura rápida del panel
    if sospechoso:
        conexion_redis.incr("cuarentena:total_sospechosos")
        for s in senales:
            conexion_redis.hincrby("cuarentena:senales", s, 1)
    else:
        conexion_redis.incr("cuarentena:total_limpios")


# Este es el arreglo que más protege el dato sin coste de UX: 100 envíos del
# mismo correo = 1 impacto, tenga la sesión que tenga. Dos alumnos = dos
# correos = dos; el mismo alumno en dos móviles = un correo = uno.
# Solo se llama cuando el evento NO es sospechoso.

def registrar_impacto_limpio(centro, ubicacion, email_hash):
    es_nuevo = conexion_redis.sadd(f"impactos_limpios:{centro}:{ubicacion}", email_hash)
    if es_nuevo == 1:
        conexion_redis.hincrby(f"stats:{centro}", ubicacion, 1)

        timestamp_actual = int(time.time())
        conexion_redis.zadd(f"timeline_ubicacion:{centro}:{ubicacion}", {email_hash: timestamp_actual})

        # Embudo fase 3 (impacto) por EMAIL, coherente con el conteo de arriba.
        # Global:
        if conexion_redis.sadd("emails_unicos_fase:3_password", email_hash) == 1:
            conexion_redis.hincrby("embudo:fase", "3_password", 1)
            conexion_redis.zadd("timeline:global:3_password", {email_hash: timestamp_actual})
        # Por facultad/centro:
        if centro and centro != "desconocido":
            if conexion_redis.sadd(f"emails_unicos_facultad:{centro}:3_password", email_hash) == 1:
                conexion_redis.hincrby(f"embudo_facultad:{centro}", "3_password", 1)
                conexion_redis.zadd(f"timeline:{centro}:3_password", {email_hash: timestamp_actual})

    return bool(es_nuevo)
