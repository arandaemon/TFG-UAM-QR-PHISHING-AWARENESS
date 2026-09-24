# 🛡️ TFG: Proyecto SEIF - Simulacro de QR Phishing (Quishing) y Concienciación

!Python Version
!Flask
!Docker
!Redis
!License

Este proyecto constituye el núcleo del servidor para la campaña de concienciación sobre **QR Phishing (Quishing)** desarrollada como Trabajo de Fin de Grado (TFG) en la Universidad Autónoma de Madrid (UAM) junto con la asociación de ciberseguridad **SEIF**. Aprobada por la Universidad Autnóma de Madrid.

La campaña consistió en el despliegue físico de códigos QR maliciosos superpuestos sobre QRs legítimos en el campus. Su objetivo principal: **realizar un estudio comparativo sobre la susceptibilidad al *Credential Harvesting* en distintos centros de la universidad**, identificando necesidades clave en concienciación digital.

---

## 📑 Índice
1. Características y Mejoras Implementadas
2. Arquitectura del Sistema
3. Estructura del Proyecto
4. Análisis de Ciberseguridad
5. Despliegue y Configuración
6. Aviso Legal

---

## ✨ Características y Mejoras Implementadas

* **Analítica Temporal y Embudo de Conversión:** Registro detallado con timestamps mediante Redis (`ZADD`, `SADD`) para auditar la caída de los usuarios en 3 fases: *Escaneo de QR, Introducción de Email e Introducción de Contraseña*.
* **Exportación de Resultados:** Panel de administración ampliado con opción de descargar informes en formato CSV, generado de manera eficiente a través de un flujo por bloques (`yield`) para evitar la sobrecarga de RAM.
* **Monitorización de Contenedores:** Instrucciones `healthcheck` integradas en Docker Compose y rutas API en Flask para garantizar la resiliencia entre el backend y Redis.
* **Logging Estructurado (JSON):** Clases de formateo personalizadas en Python para exportar todos los eventos (impactos, fallos, etc.) en formato JSON, facilitando su futura integración con sistemas de monitorización (ELK, Grafana).
* **Concienciación Reactiva e Interactiva:** Tras la captura segura de fases, el sistema redirige automáticamente a una página educativa con referencias visuales sobre el fraude.
* **Coherencia y Localización:** Todo el entorno, los formularios y el panel están forzados al español, replicando de forma nativa la experiencia promedio esperada por la mayoría del alumnado de la UAM e impidiendo sospechas por traducciones mixtas.
* **Automatización de Material Físico (Cartelería y Pegatinas):** Suite de herramientas gráficas (Tkinter) y procesamiento de imágenes (Pillow) para la generación masiva de PDFs listos para imprenta. Incrusta dinámicamente los QRs de seguimiento en múltiples diseños de carteles, organizando la salida automáticamente por facultad.

---

## 🏗️ Arquitectura del Sistema

El despliegue está diseñado bajo una arquitectura de **microservicios orquestados con Docker**, garantizando aislamiento, seguridad y alta disponibilidad.

* **Nginx (`El Escudo`):** Actúa como *Reverse Proxy* (terminación SSL/TLS). Separa el tráfico en dos dominios (`moodle.uarn.es` para el phishing y `seif.eps.uam.es` para el control), bloquea de forma silenciosa el acceso a rutas de administración en el dominio falso, restringe acceso a archivos ocultos y sirve contenido estático local.
* **Flask + Gunicorn (`El Cerebro`):** Aplicación backend en Python que gestiona la lógica de enrutamiento, flujos de suplantación (Moodle y SSO de Microsoft), protección de endpoints con CSRF dinámicos, bindeo de sesiones y generación del panel analítico.
* **Redis (`La Memoria`):** Base de datos en memoria con persistencia en disco (AOF). Gestiona sesiones seguras (evitando CWE-312) y realiza un registro atómico (evitando condiciones de carrera) de las estadísticas y timelines (ZADD/SADD).

---

## 📂 Estructura del Proyecto

```text
TFG-UAM-QR-PHISHING-AWARENESS/
├── app/
│   ├── carteles/             # Scripts (Pillow/Tkinter) para forjar carteles, pegatinas y automatizar PDFs de imprenta
│   ├── static/               # Recursos estáticos locales (CSS, JS, imágenes de Microsoft y Moodle)
│   ├── templates/            # Páginas HTML (index.html, ms_email.html, ms_password.html, admin.html, etc.)
│   ├── .dockerignore         # Exclusión de archivos sensibles para la imagen Docker
│   ├── Dockerfile            # Configuración de imagen ligera con usuario no privilegiado (appuser)
│   ├── app.py                # Setup principal, seguridad HTTP (Headers, ProxyFix) y logs en JSON
│   ├── redis_db.py           # Limitador y registro estadístico usando estructuras avanzadas en Redis
│   ├── rutas_admin.py        # Endpoints protegidos (Basic Auth) para visualizar y exportar informes CSV
│   ├── rutas_phishing.py     # Captura por fases, validación de variables y tokens CSRF dinámicos
│   ├── rutas_qrs.py          # Diccionario de seguimiento por UUID
│   ├── generador_qrs.py      # Script automatizado para la creación de QRs apuntando a los UUIDs
│   ├── requirements.txt      # Dependencias del entorno de ejecución (Gunicorn, Flask, Redis, etc.)
├── nginx/
│   └── conf.d/
│       └── default.conf      # Enrutamiento inverso, redirecciones 301, y parcheo de seguridad OpSec
├── docker-compose.yml        # Orquestador de la infraestructura y red interna (bridge)
├── LICENSE.md                # Licencia MIT
├── README.md                 # Documentación del proyecto
└── start.sh                  # Script automatizado para el despliegue del entorno
```

---

## 🔍 Análisis de Ciberseguridad y Mitigaciones

Dado su carácter institucional y su exposición en una red pública masiva, el desarrollo aplica de forma proactiva mitigaciones contra vulnerabilidades críticas (CWEs):

1. **Cumplimiento RGPD (Privacy by Design):** Las credenciales de los usuarios nunca son almacenadas. Los campos de contraseña de los formularios simulados se muestran por realismo pero **carecen de atributo `name`**, de modo que el navegador nunca transmite la contraseña al servidor. El sistema hashea únicamente la identificación (email/usuario) en memoria usando `SHA-256` combinado con un *salt* criptográfico para mantener una lista de víctimas únicas sin comprometer datos personales.
10. **Integridad del Dato (Modelo de Cuarentena):** En lugar de rechazar en duro los envíos automatizados (lo que obliga a elegir entre proteger el dato o no perder usuarios reales), cada envío se **graba con sus señales** de sospecha (tiempo infrahumano, honeypot, token ausente/reutilizado, CSRF, velocidad de correos por IP) y **solo se contabiliza si sale limpio**. La deduplicación de impactos se hace por **hash de email** (no por sesión), de modo que N envíos del mismo correo cuentan como un único impacto sin importar cuántas sesiones se generen. Todos los envíos reciben la **misma respuesta** educativa, eliminando el oráculo que revelaría a un atacante si su envío ha colado. La estadística de cabecera es, por tanto, `COUNT(DISTINCT email_hash) WHERE NOT sospechoso`, y el panel expone además la métrica de "envíos apartados" para el análisis forense.
2. **Protección Anti-DoS asimétrico (Bypass de NAT):** Utilizando `Flask-Limiter`, el límite de peticiones no se asocia a la IP de origen (ya que miles de alumnos comparten la IP pública de Eduroam, mitigando **CWE-290**), sino a un token de sesión anónimo.
3. **Prevención CSRF (Cross-Site Request Forgery):** Inyección de tokens de un solo uso generados criptográficamente. Se utiliza `secrets.compare_digest()` para mitigar *Timing Attacks*.
4. **Gestión Segura de Sesiones (CWE-312 y CWE-330):** Implementación de `Flask-Session` basado en Redis. No se envían datos críticos en cookies del cliente, y todas las cookies están firmadas y cifradas.
5. **Prevención de Condiciones de Carrera (CWE-362):** Las estadísticas se guardan usando operaciones atómicas en memoria (`setnx` y `hincrby` de Redis) para asegurar la integridad de datos frente a picos masivos de tráfico.
6. **Mitigación de Path Traversal:** Filtros sanitarios en parámetros (`/login/<uuid>`) y bloqueos duros de expresiones regulares en Nginx contra `.env`, `.git`, `.py`, `.sql` o `.yml`.
7. **Defensa en Profundidad (Contenedores):** El `Dockerfile` compila de forma aislada corriendo Gunicorn sobre un usuario sin privilegios (`appuser`), mitigando el CWE-250 ante posibles escaladas de privilegios.
8. **Resiliencia y Alta Disponibilidad:** Los recursos estáticos del portal falso se sirven localmente. Esto acelera la carga, evita alertar al SOC (Security Operations Center) de la UAM por la invocación anómala de assets, y garantiza la disponibilidad ante caídas de Moodle.
9. **Cabeceras de Seguridad y ProxyFix:** Se inyectan respuestas HTTP robustas (`Strict-Transport-Security`, `X-Frame-Options` SAMEORIGIN y `nosniff`), y se sanea la lectura de IPs de *X-Forwarded-For* limitando la confianza a Nginx utilizando el middleware `ProxyFix`.

---

##  Guía de Despliegue

### 1. Requisitos Previos
* Servidor Linux (VM local o VPS) con IP accesible (Ej. VirtualBox en Adaptador Puente).
* Tener instalados **Docker** y **Docker Compose**.

### 2. Configuración de Variables de Entorno (`.env`)
Antes de desplegar, crea un archivo `.env` en el directorio `app/` con las variables de entorno críticas. Sin este archivo, el backend se negará a arrancar por medidas de seguridad.

```env
# /app/.env
FLASK_SECRET_KEY=tu_clave_secreta_aleatoria_y_larga
SECRET_SALT=tu_salt_criptografico_para_hashing
ADMIN_USER=auditor
ADMIN_PASS=password_segura
ADMIN_PATH=dashboard-secreto

# --- Ajuste del modelo de cuarentena (opcional; valores por defecto sensatos) ---
# Tiempo mínimo (segundos) para considerar humano un envío. Como es una SEÑAL
# y no un bloqueo, puede ser alto sin castigar a usuarios reales.
UMBRAL_TIEMPO_HUMANO=2.5
# Señal de velocidad de correos nuevos por IP (desactivada por defecto para no
# penalizar el NAT de Eduroam hasta calibrarla con logs reales).
IP_SIGNAL_ACTIVA=false
IP_VENTANA_SEG=3600
IP_UMBRAL_CORREOS=20
```

### 3. Ejecución del Entorno
El proyecto incluye un script de automatización que derriba contenedores huérfanos y levanta la infraestructura limpia mostrando los logs.

```bash
chmod +x start.sh
./start.sh
```

### 4. Uso y Acceso
* **Simulación de Escaneo (Víctima):** Accede a `http://<IP_SERVIDOR>/login/<uuid>` (Sustituye `<uuid>` por un hash válido de `app/rutas.py`).
* **Panel de Auditoría (Admin):** Accede a `http://<IP_SERVIDOR>/<ADMIN_PATH>` (Definido en el `.env`) y utiliza las credenciales Basic Auth.

---

## ⚠️ Aviso Legal (Disclaimer)

Este software ha sido creado exclusivamente con fines **académicos, de concienciación y de auditoría autorizada**. El despliegue de esta plataforma contra objetivos sin su consentimiento expreso, previo y por escrito es estrictamente ilegal. La asociación **SEIF**, la Universidad Autónoma de Madrid (UAM) y el desarrollador no asumen ninguna responsabilidad por el uso indebido de este material o por daños causados a terceros.
