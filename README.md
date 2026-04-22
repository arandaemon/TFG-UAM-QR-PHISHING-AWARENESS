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

---

## 🏗️ Arquitectura del Sistema

El despliegue está diseñado bajo una arquitectura de **microservicios orquestados con Docker**, garantizando aislamiento, seguridad y alta disponibilidad.

* **Nginx (`El Escudo`):** Actúa como *Reverse Proxy* (terminación de red). Bloquea el acceso a archivos sensibles, sirve contenido estático y anonimiza la red interna.
* **Flask + Gunicorn (`El Cerebro`):** Aplicación backend en Python que gestiona la lógica de enrutamiento (escaneo de UUIDs), protección de endpoints y bindeo de sesiones.
* **Redis (`La Memoria`):** Base de datos clave-valor con persistencia en disco (AOF). Actúa como gestor de sesiones del lado del servidor seguro y registro atómico de impactos estadísticos.

---

## 📂 Estructura del Proyecto

```text
TFG-UAM-QR-PHISHING-AWARENESS/
├── app/
    │   ├── static/               # Recursos estáticos (imágenes locales, CSS indexado (independiente)
│   ├── templates/            # Plantillas HTML (Phishing, Concienciación, Panel Admin)
│   ├── .dockerignore         # Exclusión de archivos sensibles para la imagen Docker
│   ├── Dockerfile            # Construcción de la imagen Python/Gunicorn (CWE-250)
    │   ├── app.py                # Configuración principal de Flask, seguridad y logging JSON
    │   ├── redis_db.py           # Conexión a Redis y lógica para estadísticas/embudos
    │   ├── rutas_admin.py        # Panel de control y endpoints de exportación CSV (protegidos)
    │   ├── rutas_phishing.py     # Endpoints del clon de Moodle y captura de métricas
    │   ├── rutas_qrs.py          # Diccionario de mapeo de UUIDs a Facultades y Ubicaciones
│   ├── requirements.txt      # Dependencias del entorno de Python
├── nginx/
│   └── conf.d/
│       └── default.conf      # Configuración del proxy inverso y bloqueos de seguridad
├── docker-compose.yml        # Orquestador de la infraestructura y red interna (bridge)
├── LICENSE.md                # Licencia MIT
├── README.md                 # Documentación del proyecto
└── start.sh                  # Script automatizado para el despliegue del entorno
```

---

## 🔍 Análisis de Ciberseguridad y Mitigaciones

Dado su carácter institucional y su exposición en una red pública masiva, el desarrollo aplica de forma proactiva mitigaciones contra vulnerabilidades críticas (CWEs):

1. **Cumplimiento RGPD (Privacy by Design):** Las credenciales de los usuarios nunca son almacenadas. El sistema hashea la identificación (email/usuario) en memoria usando `SHA-256` combinado con un *salt* criptográfico para mantener una lista de víctimas únicas sin comprometer datos personales.
2. **Protección Anti-DoS asimétrico (Bypass de NAT):** Utilizando `Flask-Limiter`, el límite de peticiones no se asocia a la IP de origen (ya que miles de alumnos comparten la IP pública de Eduroam, mitigando **CWE-290**), sino a un token de sesión anónimo.
3. **Prevención CSRF (Cross-Site Request Forgery):** Inyección de tokens de un solo uso generados criptográficamente. Se utiliza `secrets.compare_digest()` para mitigar *Timing Attacks*.
4. **Gestión Segura de Sesiones (CWE-312 y CWE-330):** Implementación de `Flask-Session` basado en Redis. No se envían datos críticos en cookies del cliente, y todas las cookies están firmadas y cifradas.
5. **Prevención de Condiciones de Carrera (CWE-362):** Las estadísticas se guardan usando operaciones atómicas en memoria (`setnx` y `hincrby` de Redis) para asegurar la integridad de datos frente a picos masivos de tráfico.
6. **Mitigación de Path Traversal:** Filtros sanitarios en la entrada de parámetros (`/login/<uuid>`) y reglas estrictas en Nginx para denegar el acceso a archivos ocultos (`.env`, `.git`) y código fuente.
7. **Defensa en Profundidad (Contenedores):** El `Dockerfile` opera bajo un usuario sin privilegios (`appuser`), aislando el proceso en caso de que se logre ejecución remota de código (RCE). Evita **CWE-250**.
8. **Resiliencia y Alta Disponibilidad (Independencia de Origen):** Los recursos estáticos del portal clonado (CSS, SVG, PNG) se alojan y sirven localmente. Esto elimina la dependencia del servidor legítimo de Moodle, acelerando la carga, garantizando la supervivencia del panel ante caídas del servicio original y eliminando el tráfico saliente que podría alertar a los administradores de red.

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
