import os
import logging
import json
from flask import Flask
from dotenv import load_dotenv
from datetime import timedelta
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv() # Carga las variables de entorno desde el archivo .env

# CONFIGURACIÓN DE LOGS ESTRUCTURADOS (JSON)
class JSONFormatter(logging.Formatter):
    def format(self, record):
        # Log por defecto
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName
        }
        
        # Extraemos atributos dinámicos pasados en el parámetro 'extra'
        # En standard keys metemos toda la basura que no nos gusta
        standard_keys = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename', 
            'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName', 
            'created', 'msecs', 'relativeCreated', 'thread', 'threadName', 'processName', 
            'process', 'message', 'asctime', 'taskName'
        }
        for key, value in record.__dict__.items():
            if key not in standard_keys:
                if isinstance(value, (str, int, float, bool, type(None))):
                    log_record[key] = value
                else:
                    log_record[key] = str(value)

        if record.exc_info:
            log_record["error"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

json_handler = logging.StreamHandler()
json_handler.setFormatter(JSONFormatter())
#  partir de ahora forzamos a Flask a usar nuestro sistema de logs
logging.basicConfig(level=logging.INFO, handlers=[json_handler], force=True)
# --------------------------------------------------

# Importamos db, limitador y rutas después de cargar las variables de entorno
from redis_db import conexion_redis, limiter
from rutas_phishing import phishing_bp
from rutas_admin import admin_bp

app = Flask(__name__)
# Para registrar IPS reales y evitar conflictos entre https y http
# Limito a uno para evitar el (CWE-290)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Cargamos la clave de la variable de entorno
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
secret_salt = os.environ.get("SECRET_SALT")

if not app.secret_key or not secret_salt:
    logging.critical("FLASK_SECRET_KEY o SECRET_SALT no configuradas", extra={"event_type": "startup_error"})
    raise RuntimeError("CRÍTICO: FLASK_SECRET_KEY o SECRET_SALT no están configuradas en las variables de entorno.")

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = conexion_redis
app.config['SESSION_USE_SIGNER'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
Session(app)

limiter.init_app(app)

# CABECERAS DE SEGURIDAD 
@app.after_request
def añadir_seguridad(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Ruta para comprobar si los contenedores siguen activos
@app.route('/health')
def health_check():
    health_data = {
        "status": "healthy",
        "dependencies": {
            "redis": "unhealthy"
        }
    }
    try:
        conexion_redis.ping()
        health_data["dependencies"]["redis"] = "healthy"
        return health_data, 200
    except Exception as e:
        logging.error("Error en health check (Redis)", extra={"error_details": str(e), "event_type": "healthcheck_failure"})
        health_data["status"] = "unhealthy"
        return health_data, 503

# He usado flask blueprint para modularizar el código
app.register_blueprint(phishing_bp)
app.register_blueprint(admin_bp)