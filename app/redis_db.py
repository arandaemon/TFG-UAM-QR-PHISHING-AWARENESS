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
    ''' Función para detectar hasta 
        que fase llegó el engaño (embudo)
        Fases: '1_qr', '2_email', '3_password'
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

# Función que almacena tanto los stats como los participantes en redis
def registrar_victima(centro, ubicacion, identificador_hash):
    clave_participante = f"participante:{identificador_hash}"
    es_nuevo = conexion_redis.setnx(clave_participante, 1)
    
    if es_nuevo:
        # Le ponemos un tiempo de enfriamiento de 24 horas
        conexion_redis.expire(clave_participante, 86400)
        
    # Extraemos el identificador de sesión de forma segura
    visitor_id = session.get('visitor_id') or session.get('limiter_id')
        
    # Comprobamos si esta sesión ya ha generado un impacto en esta ubicación
    es_nuevo_impacto = conexion_redis.sadd(f"visitantes_unicos_ubicacion:{centro}:{ubicacion}", visitor_id)
    if es_nuevo_impacto == 1:
        conexion_redis.hincrby(f"stats:{centro}", ubicacion, 1)
        
        # Registramos también el timestamp en la línea temporal de esta ubicación
        timestamp_actual = int(time.time())
        conexion_redis.zadd(f"timeline_ubicacion:{centro}:{ubicacion}", {visitor_id: timestamp_actual})
        
    return bool(es_nuevo)
