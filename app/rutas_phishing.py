import logging
import secrets
from flask import Blueprint, render_template, session, abort, request, redirect, url_for
from rutas_qrs import MAPEO_TRACKING
from redis_db import detector_de_fases, registrar_victima, convertir_email_hash, limiter, conexion_redis
import time
import re

# Para evitar que alguien se le ocurra usar un correo que no sea de la UAM para probar el sistema,
PATRON_CORREO_UAM = re.compile(r'^[a-zA-Z0-9_.+-]+@(estudiante\.uam\.es|uam\.es)$')

phishing_bp = Blueprint('phishing', __name__)

@phishing_bp.route('/login/<string:uuid>')
def index_qr(uuid):
    # Bloqueo cualquier intento de usar puntos o barras para navegar por el sistema
    if ".." in uuid or "/" in uuid or "\\" in uuid:
        logging.warning(
            "ALERTA DE SEGURIDAD: Intento de Path Traversal detectado",
            extra={"ip": request.remote_addr, "uuid": uuid, "event_type": "path_traversal"}
        )
        abort(400)
        
    # Creamos un identificador único para este visitante específico
    # Para evitar que se recargue la página 100 veces y se cuenten como
    # Escaneos de Qr
    if 'visitor_id' not in session:
        session['visitor_id'] = secrets.token_hex(16)
    
    # Buscamos en el diccionario
    datos_contexto = MAPEO_TRACKING.get(uuid)
    
    if datos_contexto is None:
        abort(404)
    
    session['centro'] = datos_contexto['centro']
    session['ubicacion'] = datos_contexto['ubicacion']

    return redirect(url_for('phishing.portal_principal'))

@phishing_bp.route('/login/index.php')
def portal_principal():

    # Si no hay centro en sesión, no vino por un QR → 404
    if not session.get('centro'):
        abort(404)

    # Generamos el token de un solo uso
    token_antienvenenamiento = secrets.token_urlsafe(16)
    # Guardamos en Redis: clave con TTL de 15 minutos (900s) y valor = hora exacta actual
    conexion_redis.set(f"tok_form:{token_antienvenenamiento}", time.time(), ex=900)

    token_csrf = secrets.token_hex(16)
    session['csrf_token'] = token_csrf
    
    # Registramos que el usuario ha llegado
    # Hasta esta fase
    centro = session.get('centro', 'desconocido')
    detector_de_fases('1_qr', centro)
    
    return render_template('index.html',  csrf_token=token_csrf, token_antienvenenamiento=token_antienvenenamiento)

@phishing_bp.route('/login.microsoftonline.com/fc6602ef-8e88-4f1d-a206-e14a3bc19af2/saml2')
def ms_login():

    # Si no hay centro en sesión, no vino por un QR → 404
    if not session.get('centro'):
        abort(404)

    return render_template('ms_email.html')

@phishing_bp.route('/login.microsoftonline.com/fc6602ef-8e88-4f1d-a206-e14a3bc19af2/saml3', methods=['POST'])
def ms_password():

    # Si no hay centro en sesión, no vino por un QR → 404
    if not session.get('centro'):
        abort(404)

    correo = request.form.get('email')

    # Validamos que el correo sea del dominio UAM antes de continuar
    if not correo or not PATRON_CORREO_UAM.match(correo):
        logging.warning(
            "VALIDACION FALLIDA EN PASO EMAIL: correo fuera del dominio UAM",
            extra={"ip": request.remote_addr, "event_type": "invalid_email_domain"}
        )
        return render_template('ms_email_error.html')

    session['email'] = correo
    
    token_csrf = secrets.token_hex(16) 
    session['csrf_token'] = token_csrf 

    # TOKEN ANTI-ENVENENAMIENTO (para el login de Microsoft)
    tok_antienvenenamiento = secrets.token_urlsafe(16)
    conexion_redis.set(f"tok_form:{tok_antienvenenamiento}", time.time(), ex=900)
    
    # Registramos que el usuario ha llegado
    # Hasta esta fase
    centro = session.get('centro', 'desconocido')
    detector_de_fases('2_email', centro)
    
    return render_template('ms_password.html', csrf_token=token_csrf, token_antienvenenamiento=tok_antienvenenamiento)

@phishing_bp.route('/validar', methods=['POST'])
@limiter.limit("5 per minute") # Límite por SESIÓN, no por IP.
def validar():

    # Si no hay centro en sesión, no vino por un QR → 404
    if not session.get('centro'):
        abort(404)

    # Recuperamos y DESTRUIMOS el token a la vez (operación atómica)
    token_recibido = request.form.get('token_form', '')
    tiempo_creacion = conexion_redis.getdel(f"tok_form:{token_recibido}")

    # Si no existe, ya fue usado, está vacío o ha caducado
    if not tiempo_creacion:
        logging.warning("RECHAZADO: Token inexistente o reutilizado.", extra={"ip": request.remote_addr})
        return render_template('concienciacion_repetido.html')

    # Control de tiempo humano, nadie lee y envía en menos de 2.5 segundos
    tiempo_transcurrido = time.time() - float(tiempo_creacion)
    if tiempo_transcurrido < 1.0:
        logging.warning(
            "RECHAZADO: Envío automatizado ultrarrápido", 
            extra={"tiempo": tiempo_transcurrido, "ip": request.remote_addr}
        )
        return render_template('concienciacion_repetido.html')

    # Honeypot para bots tontos que rellenan todos los campos de un formulario sin mirar
    if request.form.get('website'):
        logging.warning(
            "RECHAZADO: Honeypot activado (relleno automático de campos)",
            extra={"ip": request.remote_addr, "event_type": "honeypot"}
        )
        return render_template('concienciacion_repetido.html')
    
    # Si esta sesión ya ha caído una vez le mostramos la página de concienciación para repetidores
    if session.get('compromised'):
        logging.info("BLOQUEO OPSEC: Intento repetido de sesión comprometida", extra={"ip": request.remote_addr})
        return render_template('concienciacion_repetido.html')
    
    es_nuevo = False
    centro = session.get('centro', 'desconocido')
    ubicacion = session.get('ubicacion', 'desconocida')
    email = session.get('email') 
    username = request.form.get('username') 
    token_en_sesion = session.get('csrf_token')
    token_del_formulario = request.form.get('csrf_token')

    if not token_en_sesion or not token_del_formulario or not secrets.compare_digest(token_en_sesion, token_del_formulario):
        logging.warning(
            "FALLO CSRF: Intento de validación sin token válido.",
            extra={"ip": request.remote_addr, "event_type": "csrf_failure"}
        )
        abort(403)
        
    session.pop('csrf_token', None)
    identificador = email if email else username

    # Para evitar que alguien use un correo que no sea de la UAM, validamos el dominio del correo
    if not identificador or not PATRON_CORREO_UAM.match(identificador):
        logging.warning(
            "VALIDACION FALLIDA: correo fuera del dominio UAM o vacío",
            extra={"ip": request.remote_addr, "event_type": "invalid_email_domain"}
        )
        return render_template('index.html', csrf_token=secrets.token_hex(16))
    
    identificador_hash = convertir_email_hash(identificador)
    es_nuevo = registrar_victima(centro, ubicacion, identificador_hash)
    if email:
        logging.info("IMPACTO REGISTRADO", extra={"plataforma": "Microsoft", "centro": centro, "ubicacion": ubicacion, "event_type": "phishing_impact"})
    elif username:
        logging.info("IMPACTO REGISTRADO", extra={"plataforma": "Moodle", "centro": centro, "ubicacion": ubicacion, "event_type": "phishing_impact"})
   
    # Si el usuario utilizó el formulario de Moodle (Otros usuarios)
    # directamente desde el index, no pasó por la ruta intermedia (fase 2).
    # Al registrarla aquí, Redis (gracias a los Sets) la sumará si le faltaba,
    # pero la ignorará y evitará duplicados si ya venía del flujo de Microsoft.
    detector_de_fases('2_email', centro)
    detector_de_fases('3_password', centro)
    
    # Marcamos la sesión como comprometida antes de limpiar las variables
    session['compromised'] = True
            
    session.pop('centro', None)
    session.pop('ubicacion', None)
    session.pop('email', None)
    
    return render_template('concienciacion.html') if es_nuevo else render_template('concienciacion_repetido.html')

# Ruta auxiliar para facilitar las pruebas durante el desarrollo
#@phishing_bp.route('/reset')
#def reset_sesion():
    #session.clear() # Borra el visitor_id, el limiter_id y todo lo demás
    # Para que funcione bien la prueba, redirigimos automáticamente a un QR válido
    # En este caso, simularemos el escaneo en la Facultad de Ciencias (Cafetería)
    #return redirect(url_for('phishing.index_qr', uuid='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'))