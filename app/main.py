import os
import redis # Driver de Redis
from flask import Flask, render_template, session, abort, request, redirect, url_for
from dotenv import load_dotenv
from datetime import timedelta
from rutas import MAPEO_TRACKING
from flask_limiter import Limiter
from flask_session import Session # Importamos el gestor de sesiones del lado del servidor
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Response # Necesario para el mensaje de login del navegador
from functools import wraps
import secrets
import hashlib
import logging

app = Flask(__name__)
# Para registrar IPS reales y evitar conflictos entre https y http
# Limito a uno para evitar el (CWE-290)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

load_dotenv() # Carga las variables de entorno desde el archivo .env

# Cragamos la clave de la variable de entorno
# Si no esta tenemos fallback generado en el momento
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
secret_salt = os.environ.get("SECRET_SALT")

# Comprobamos que se hayan cargado ambas variables de entorno
if not app.secret_key or not secret_salt:
    logging.critical("CRÍTICO: FLASK_SECRET_KEY o SECRET_SALT no están configuradas.")
    raise RuntimeError("CRÍTICO: FLASK_SECRET_KEY o SECRET_SALT no están configuradas en las variables de entorno.")

# Mitigación de CWE-312
# Al usar redis, los datos sensibles (email, centro, tokens) no se envían 
# al navegador en la cookie, evitando su exposición en el lado del cliente.
# Configuramos la conexión a Redis gracias al DNS interno de Docker Compose
conexion_redis = redis.from_url('redis://redis:6379')
# Le decimos a la app que use redis para guardar las sesiones
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = conexion_redis
# Para que tambien se firmen las cookies y evitar
# Ataques de fuerza bruta a la base de datos (CWE-330)
app.config['SESSION_USE_SIGNER'] = True
# Evita que Redis se llene (DoS) si un bot genera miles de sesiones sin cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
Session(app)

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
    obtener_id_sesion,
    app=app,
    storage_uri="redis://redis:6379",
    strategy="fixed-window"
)

# CABECERAS DE SEGURIDAD 
@app.after_request
def añadir_seguridad(response):
    # Evita que la web sea cargada en un iframe 
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # Evita que el navegador intente adivinar el tipo de contenido 
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Fuerza el uso de HTTPS en el navegador del cliente
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


def requiere_auth(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        auth = request.authorization
        user_env = os.environ.get("ADMIN_USER")
        pass_env = os.environ.get("ADMIN_PASS")
        
        if not auth or not (auth.username == user_env and auth.password == pass_env):
            # Si no hay auth, devolvemos un 401 (Unauthorized) 
            # Esto dispara la ventanita de usuario/pass en el navegador
            return Response(
                'Acceso denegado. Introduce credenciales.', 401,
                {'WWW-Authenticate': 'Basic realm="Login de Administrador"'}
            )
        return f(*args, **kwargs)
    return decorada

# Convierte el email a un hash
def convertir_email_hash(email):
    # Pasar email a limpio
    email_limpio = email.lower().strip() 
    # Cocatenamos el salt secreto
    datos_a_hashear = f"{secret_salt}{email_limpio}".encode('utf-8')
    # Creamos el hash con un salt secreto
    email_hash = hashlib.sha256(datos_a_hashear).hexdigest()
    
    return email_hash

# Función que al,macena tanto los stast como los participantes en redis
def registrar_victima(centro, ubicacion, identificador_hash):
    # Guardamos el hash del identificador
    clave_participante = f"participante:{identificador_hash}"
    # Incrementamos el valor
    # Si es nuevo devuelve 1, si ya existía devuelve 0
    es_nuevo =conexion_redis.setnx(clave_participante, 1)
    
    # Si es nuevo incrementamos stats
    if es_nuevo:
        # Le ponemos un tiempo de enfriamiento de 24 horas
        # Para evitar que se nos llene la RAM (redis corre en RAM)
        conexion_redis.expire(clave_participante, 86400)
        # Buscamos por clave el diccionario en Redis
        clave_stats = f"stats:{centro}"
        # Incrementamos el valor segun subclave (es atómico)
        conexion_redis.hincrby(clave_stats, ubicacion, 1)
        return True # Se sumó a la estadística
    else:
        return False # El alumno ya había caído antes, ignoramos la petición
        
        
@app.route('/login/<string:uuid>')
def index_qr(uuid):
    # Bloqueo cualquier intento de usar puntos o barras para navegar por el sistema
    if ".." in uuid or "/" in uuid or "\\" in uuid:
        # Usamos logging.warning porque es un evento de seguridad anómalo, 
        # print es más dificil de procesar
        logging.warning(f"ALERTA DE SEGURIDAD: Intento de Path Traversal detectado desde IP {request.remote_addr} con UUID: {uuid}")
        abort(400)
    
    # Buscamos en el diccionario
    datos_contexto = MAPEO_TRACKING.get(uuid)
    
    if datos_contexto is None:
        abort(404)
    
    session['centro'] = datos_contexto['centro']
    session['ubicacion'] = datos_contexto['ubicacion']

    return redirect(url_for('portal_principal'))

@app.route('/login/index.php')
def portal_principal():
    token_csrf = secrets.token_hex(16)
    session['csrf_token'] = token_csrf
    return render_template('index.html', csrf_token=token_csrf)

@app.route('/login.microsoftonline.com/fc6602ef-8e88-4f1d-a206-e14a3bc19af2/saml2')
def ms_login():
    # Mostrar pantalla de correo de Microsoft
    return render_template('ms_email.html')

@app.route('/login.microsoftonline.com/fc6602ef-8e88-4f1d-a206-e14a3bc19af2/saml3', methods=['POST'])
def ms_password():
    # Capturamos el correo que viene del 'name="email"' del HTML
    correo = request.form.get('email')
    # Lo guardamos en la sesión para usarlo en la siguiente pantalla
    session['email'] = correo
    
    # Esto evita que alguien pueda enevenenar nuestros datos
    # Con llamadas de terceros
    token_csrf = secrets.token_hex(16) # Genera una cadena aleatoria de 32 caracteres
    session['csrf_token'] = token_csrf # La guardamos en su bóveda (cookie firmada)
    
    # Cargamos la página de la contraseña
    return render_template('ms_password.html', csrf_token=token_csrf)

@app.route('/validar', methods=['POST'])
@limiter.limit("5 per minute") # Límite por SESIÓN, no por IP. Permite errores humanos, bloquea ráfagas de bots.
def validar():
    es_nuevo = False
    # Recuperamos la facultad que guardamos al principio de todo (QR)
    centro = session.get('centro', 'desconocido')
    ubicacion = session.get('ubicacion', 'desconocida')
    
    # Capturamos las credenciale
    email = session.get('email') # Del flujo de Microsoft
    username = request.form.get('username') # Del flujo de Moodle
    
    # El token que creamos
    token_en_sesion = session.get('csrf_token')
    # El que viene del formulario
    token_del_formulario = request.form.get('csrf_token')

    # Usamos secrets.compare_digest para evitar ataques de temporización 
    if not token_en_sesion or not token_del_formulario or not secrets.compare_digest(token_en_sesion, token_del_formulario):
        logging.warning(f"FALLO CSRF: IP {request.remote_addr} intentó validar sin token válido.")
        abort(403) # 403 Forbidden: Acceso denegado
        
    # Consumimos el token. Así evitamos ataques de repetición 
    session.pop('csrf_token', None)
    
    # Identificamos si hemos obtenido email o username
    identificador = email if email else username
    
    # Registramos el éxito en Redis
    
    if identificador:
        # Convertimos el identificador a hash
        identificador_hash = convertir_email_hash(identificador)
    
        es_nuevo = registrar_victima(centro, ubicacion, identificador_hash)
        
        # Logging para el auditor
        if email:
            logging.info(f"IMPACTO en Microsoft: Centro: {centro}, Ubicación: {ubicacion}")
        elif username:
            logging.info(f"IMPACTO en Moodle: Centro: {centro}, Ubicación: {ubicacion}")
        else:
            logging.warning(f"IMPACTO (Desconocido): Se recibió una petición vacía desde IP {request.remote_addr}")
            
    # Limpiamos solo los datos del impacto para no dejar rastro, 
    # pero conservamos el limiter_id para que el firewall asimétrico siga funcionando.
    session.pop('centro', None)
    session.pop('ubicacion', None)
    session.pop('email', None)
    
    return render_template('concienciacion.html') if es_nuevo else render_template('concienciacion_repetido.html')

# ESTADÍSTICAS
@app.route(f"/{os.environ.get('ADMIN_PATH', 'admin-default')}")
@requiere_auth
def admin_stats():
    claves = conexion_redis.keys("stats:*")
    todas_las_stats = {}

    for clave in claves:
        # Decodificamos de bytes a string (UTF-8) para evitar errores de tildes
        nombre_facultad = clave.decode('utf-8').replace("stats:", "")
        datos_raw = conexion_redis.hgetall(clave)
        
        # Diccionario de comprensión para limpiar los datos de Redis
        datos_limpios = {k.decode('utf-8'): int(v.decode('utf-8')) for k, v in datos_raw.items()}
        todas_las_stats[nombre_facultad] = datos_limpios

    return render_template('admin.html', stats=todas_las_stats)

@app.route(f"/cerrar-sesion")
@requiere_auth
def admin_cerrar_sesion():
    # Enviar un 401 obliga al navegador a olvidar las credenciales cacheadas de Basic Auth
    return Response(
        'Sesión de administrador cerrada correctamente. Por favor, cierra esta pestaña por mayor seguridad.', 401,
        {'WWW-Authenticate': 'Basic realm="Login de Administrador"'}
    )

    
    
if __name__ == "__main__":
    app.run(host= '0.0.0.0', port=8000)