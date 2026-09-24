import logging
import secrets
from flask import Blueprint, render_template, session, abort, request, redirect, url_for
from rutas_qrs import MAPEO_TRACKING
from redis_db import (
    detector_de_fases,
    convertir_email_hash,
    registrar_evento_cuarentena,
    registrar_impacto_limpio,
    senal_velocidad_ip,
    limiter,
    conexion_redis,
    UMBRAL_TIEMPO_HUMANO,
)
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
@limiter.limit("5 per minute") # Límite por SESIÓN (anti-flood), no por IP.
def validar():

    # Si no hay centro en sesión, no vino por un QR → 404
    # (Esto es un guard de enrutamiento, igual para todos: no revela nada
    #  sobre si un envío "contó" o no, así que no crea oráculo.)
    if not session.get('centro'):
        abort(404)

    centro = session.get('centro', 'desconocido')
    ubicacion = session.get('ubicacion', 'desconocida')
    ip = request.remote_addr

    # ------------------------------------------------------------------
    # MODELO DE CUARENTENA: calculamos TODAS las señales sin rechazar en
    # duro. Marcar != bloquear. El evento se grabará siempre; solo se
    # CONTARÁ como impacto si sale limpio. Así podemos ser sensibles con el
    # tiempo humano sin perder a nadie real.
    # ------------------------------------------------------------------
    senales = []

    # SEÑAL 1: token anti-envenenamiento ausente/caducado/reutilizado.
    # Lo recuperamos y DESTRUIMOS a la vez (operación atómica).
    token_recibido = request.form.get('token_form', '')
    tiempo_creacion = conexion_redis.getdel(f"tok_form:{token_recibido}") if token_recibido else None
    if not tiempo_creacion:
        senales.append('token')
    else:
        # SEÑAL 2: tiempo demasiado rápido para ser humano. Al ser señal
        # (no bloqueo) el umbral puede ser alto sin castigar a nadie.
        tiempo_transcurrido = time.time() - float(tiempo_creacion)
        if tiempo_transcurrido < UMBRAL_TIEMPO_HUMANO:
            senales.append('tiempo')

    # SEÑAL 3: honeypot (campo oculto que solo rellenan los bots).
    if request.form.get('website'):
        senales.append('honeypot')

    # SEÑAL 4: CSRF ausente/no coincidente. Aquí no protege un estado
    # sensible (no hay login real): lo usamos como heurística de bot, así
    # que lo tratamos como señal en vez de abortar (evita crear oráculo).
    token_en_sesion = session.get('csrf_token')
    token_del_formulario = request.form.get('csrf_token')
    if not token_en_sesion or not token_del_formulario or not secrets.compare_digest(token_en_sesion, token_del_formulario):
        senales.append('csrf')
    session.pop('csrf_token', None)

    # Identificador: email del flujo Microsoft, o usuario del flujo Moodle.
    email = session.get('email')
    username = request.form.get('username')
    identificador = email if email else username

    # SEÑAL 5: identificador vacío o fuera del dominio UAM. No es un impacto
    # medible del estudio, pero lo grabamos igual (sin descartarlo del todo).
    identificador_valido = bool(identificador and PATRON_CORREO_UAM.match(identificador))
    if not identificador_valido:
        senales.append('email_invalido')

    # Hash del identificador (para dedup y forense). Si no hay, cadena vacía.
    identificador_hash = convertir_email_hash(identificador) if identificador else ""

    # SEÑAL 6: velocidad de correos nuevos por IP (desactivada por defecto).
    if identificador_hash and senal_velocidad_ip(ip, identificador_hash):
        senales.append('ip')

    sospechoso = bool(senales)

    # Grabamos SIEMPRE en la cuarentena (limpio o sospechoso): fuente de
    # verdad y base de la métrica "N envíos apartados" para la memoria.
    registrar_evento_cuarentena(identificador_hash, centro, ubicacion, ip, sospechoso, senales)

    # Solo contamos el impacto si el evento sale LIMPIO y el email es válido.
    if not sospechoso and identificador_valido:
        registrar_impacto_limpio(centro, ubicacion, identificador_hash)
        plataforma = "Microsoft" if email else "Moodle"
        logging.info(
            "IMPACTO REGISTRADO",
            extra={"plataforma": plataforma, "centro": centro, "ubicacion": ubicacion, "event_type": "phishing_impact"}
        )
    else:
        logging.warning(
            "EVENTO EN CUARENTENA",
            extra={"senales": ",".join(senales), "centro": centro, "ubicacion": ubicacion, "ip": ip, "event_type": "cuarentena"}
        )

    # Embudo de EXPOSICIÓN (visitas): quien envía el formulario ha llegado a
    # la fase de credenciales. El flujo Moodle "Otros usuarios" no pasa por
    # la ruta intermedia (fase 2), así que la registramos aquí; los Sets
    # evitan duplicados si ya venía del flujo Microsoft.
    detector_de_fases('2_email', centro)

    # Limpiamos las variables sensibles de la sesión.
    session.pop('centro', None)
    session.pop('ubicacion', None)
    session.pop('email', None)

    # RESPUESTA ÚNICA para todos: mata el oráculo (antes concienciacion.html
    # vs concienciacion_repetido.html le decía al atacante si había colado) y
    # sigue educando también al usuario dudoso.
    return render_template('concienciacion.html')

# Ruta auxiliar para facilitar las pruebas durante el desarrollo
#@phishing_bp.route('/reset')
#def reset_sesion():
    #session.clear() # Borra el visitor_id, el limiter_id y todo lo demás
    # Para que funcione bien la prueba, redirigimos automáticamente a un QR válido
    # En este caso, simularemos el escaneo en la Facultad de Ciencias (Cafetería)
    #return redirect(url_for('phishing.index_qr', uuid='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'))