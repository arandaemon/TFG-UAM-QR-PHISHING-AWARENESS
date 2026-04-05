---

# 🛡️  Proyecto SEIF: Simulacro de Phishing y Concienciación (UAM)

Este proyecto es el núcleo del servidor de la campaña de concienciación sobre **QR Phishing (Quishing)** llevada a cabo en la Universidad Autónoma de Madrid (UAM) por la asociación de estudiantes de ciberseguridad **SEIF**. 

La campaña, supervisada estrechamente por la **Subdirectora de la EPS** y los **encargados de ciberseguridad de la universidad**, consistió en el despliegue de carteles atractivos y la colocación de pegatinas con códigos QR maliciosos superpuestas sobre QR legítimos en el campus. El objetivo principal ha sido realizar un estudio comparativo entre varios centros de la universidad para evaluar su nivel de concienciación frente a ataques de *Credential Harvesting* e identificar qué facultades requieren mayor atención en materia de ciberseguridad.

## 🏗️  Arquitectura del Sistema

El despliegue se basa en una arquitectura de **microservicios orquestados con Docker**, garantizando el aislamiento del entorno y la escalabilidad de la recolección de datos.

* **Nginx (Reverse Proxy):** Actúa como primera línea de defensa y terminación de red. Gestiona el tráfico estático y anonimiza el backend.
* **Flask (Logic Tier):** Motor en Python que gestiona la lógica de las rutas (vía escaneo de QR), el bindeo de sesiones y las protecciones contra ataques.
* **Redis (Session & Stats Database):** Base de datos en memoria (AOF activado) utilizada para gestionar de forma segura las sesiones de los usuarios (lado servidor) y almacenar atómicamente las estadísticas de impacto de la campaña.

---

## 🛠️ Stack Tecnológico y Configuración

| Componente | Tecnología | Razón Técnica |
| :--- | :--- | :--- |
| **Backend** | Python 3.11-slim | Imagen ligera para reducir la superficie de ataque del contenedor. |
| **Servidor App** | Flask + ProxyFix | Corrección segura de cabeceras para registrar la IP real detrás del reverse proxy de Nginx. |
| **Persistencia** | Redis (Alpine) | Almacenamiento en memoria ultrarrápido y seguro del estado de las sesiones e incrementos estadísticos concurrentes. |
| **Frontend** | HTML5 / CSS3 | Réplica exacta usando unidades `rem` y tipografías del sistema (Segoe UI/Arial). |

---

## 🚀 Guía de Despliegue Rápido (Cheat Sheet)

### 1. Preparación de la VM (VirtualBox)
* **Red:** Adaptador Puente (Bridged) -> `Intel(R) Wireless-AC 9560`.
* **IP Local:** Obtener con `hostname -I` (ej. `192.168.228.28`).
* **Firewall:** `sudo ufw disable` (solo para pruebas locales).

### 2. Comandos de Ejecución
```bash
# Ejecutar el script de inicialización automática (limpia contenedores e inicia la infraestructura)
./start.sh
```

### 3. URL de Acceso
`http://<IP_VM>:8000/login/<uuid_del_qr>`
*Nota: El UUID corresponde a los identificadores criptográficos mapeados en `rutas.py` para cada ubicación específica (cafetería, biblioteca, baños) de cada centro.*

---

## 🔍 Análisis de Ciberseguridad (Forense y Ofensivo)

Dado su carácter institucional y su exposición a una red pública masiva, el servidor incorpora las siguientes mitigaciones proactivas:

1.  **Protección de Datos (Cumplimiento RGPD):** Las credenciales y usuarios capturados jamás se almacenan ni registran.
2.  **Prevención de Ataques de Temporización (Timing Attacks):** Validación segura de tokens CSRF usando la función `secrets.compare_digest()`.
3.  **Bypass de NAT Institucional (Eduroam):** Implementación asimétrica de `Flask-Limiter` basada en tokens de sesión en lugar de IPs. Esto previene el bloqueo masivo (DoS) de usuarios legítimos que salen por la misma IP pública de la universidad.
4.  **Prevención de Race Conditions (CWE-362):** Uso de comandos atómicos en memoria mediante `Redis` (`hincrby`) para garantizar la integridad absoluta de las estadísticas frente a ráfagas de escaneos concurrentes (ej. durante los cambios de clase).
5.  **Path Traversal y Clickjacking:** Filtros estrictos en los UUID dinámicos y aplicación sistemática de cabeceras de seguridad (`X-Frame-Options`, `X-Content-Type-Options`, `HSTS`).


---

## ⚠️  Aviso Legal (Disclaimer)

Este software ha sido creado exclusivamente con fines **académicos y de auditoría autorizada**. El uso de esta herramienta contra objetivos sin autorización previa y por escrito es estrictamente ilegal y constituye un delito informático. La asociación **SEIF** y los autores no se hacen responsables del mal uso de este código.

---

**¿Te gustaría que añadamos una sección específica sobre cómo el servidor gestiona las cabeceras de seguridad HSTS o CSP para hacerlo aún más "pro"?** Sería el siguiente nivel de blindaje para tu servidor Nginx.
