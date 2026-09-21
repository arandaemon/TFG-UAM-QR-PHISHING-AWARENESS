
---

# Despliegue y Configuración del Sistema de Prevención de Intrusos (IPS) con Fail2ban y Docker

## 1. Justificación Arquitectónica: ¿Por qué Fail2ban en el Anfitrión?

En una arquitectura contenerizada donde Nginx y la aplicación Flask operan dentro de Docker, surge un desafío crítico de diseño a la hora de implementar contramedidas de seguridad perimetral: **¿Dónde debe instalarse Fail2ban?**

La respuesta correcta para un entorno de producción o despliegue robusto es instalar Fail2ban **directamente en el sistema operativo anfitrión (Host)** y no dentro de los contenedores Docker. Los motivos técnicos son los siguientes:

* **Acceso directo al Kernel y Netfilter (`iptables`):** Fail2ban opera modificando las reglas del cortafuegos del kernel de Linux para descartar tráfico a nivel de red (`DROP`). Los contenedores Docker están aislados mediante namespaces y, por defecto, no deben ni pueden manipular las tablas de enrutamiento globales del host de forma nativa sin privilegios excesivos (`--privileged`), lo cual comprometería la seguridad del contenedor.
* **Persistencia y Ciclo de Vida:** Si Fail2ban residiera dentro del contenedor de Nginx, cualquier actualización, reconstrucción (`docker compose build`) o caída del contenedor destruiría el estado del servicio de seguridad y el historial de baneos activos. El anfitrión garantiza un ciclo de vida persistente independiente de los contenedores.
* **Persistencia de Logs mediante Volúmenes:** Nginx escribe sus registros de errores en un volumen compartido con el host (`./nginx/logs/error.log`). El demonio de Fail2ban en el anfitrión puede monitorizar este archivo físico en tiempo real utilizando el backend de `polling`, evitando dependencias complejas con los daemons de logging de Docker.

---

## 2. Guía de Instalación y Configuración Paso a Paso

### Paso 1: Instalación de Fail2ban en el Sistema Operativo

Actualiza los repositorios e instala Fail2ban en el host (en este caso, sobre un entorno Ubuntu/Debian):

```bash
sudo apt update
sudo apt install fail2ban -y

```

### Paso 2: Configuración del Filtro de Nginx para Rate Limiting

Crea un archivo de filtro personalizado para que Fail2ban sepa exactamente qué patrón buscar en el archivo de registro de errores de Nginx cuando se desborde el límite de peticiones (exceso en la zona `login_qr`).

Crea el archivo `/etc/fail2ban/filter.d/nginx-limit-req.conf`:

```ini
[Definition]
failregex = ^%(__prefix_line)s\s*\[error\] \d+#\d+: \*\d+ limiting requests, excess: .+\., client: <HOST>, server: \S+, request: "[^"]+", host: "[^"]+"
ignoreregex =

```

### Paso 3: Definición de la Jaula (Jail) con Acciones Personalizadas para Docker

Dado que Docker gestiona el tráfico de red mediante reglas de reenvío NAT en la cadena `DOCKER-USER`, las acciones estándar de Fail2ban (diseñadas para la cadena `INPUT`) no interceptarían el tráfico de los contenedores. Para solucionar esto, creamos una **acción personalizada** que aplique un bloqueo absoluto (`DROP`) directamente en la primera posición de la cadena de Docker.

Crea el archivo de acción personalizado en `/etc/fail2ban/action.d/docker-drop.conf`:

```ini
[Definition]
actionstart = 
actionstop = 
actioncheck = 
actionban = iptables -I DOCKER-USER 1 -s <ip> -j DROP
actionunban = iptables -D DOCKER-USER -s <ip> -j DROP

```

### Paso 4: Activación de la Jaula en `jail.local`

Configura la jaula perimetral en el archivo `/etc/fail2ban/jail.local` apuntando al volumen de logs de tu proyecto Docker y utilizando la acción `docker-drop`:

```ini
[nginx-ratelimit]
enabled  = true
port     = http,https
filter   = nginx-limit-req
backend  = polling
logpath  = /home/seif/tfg-qr-phishing/nginx/logs/error.log
banaction = docker-drop
maxretry = 15
findtime = 10
bantime  = 5m

```

*(Nota: Ajusta la ruta de `logpath` según la ubicación absoluta de tu proyecto en el servidor).*

### Paso 5: Reinicio y Verificación del Servicio

Una vez guardadas las configuraciones, reinicia el demonio de Fail2ban para aplicar los cambios en el kernel:

```bash
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

```

Para comprobar que el servicio está activo y monitorizando correctamente las reglas de la jaula, ejecuta:

```bash
sudo fail2ban-client status nginx-ratelimit

```

Aquí tienes la sección final ampliada con los comandos prácticos de prueba, simulación de ataques y auditoría de baneos, lista para integrarla en tu documento del TFG:

---

## 3. Pruebas de Validación y Auditoría del Sistema de Defensa

Una vez desplegado el sistema, es fundamental verificar su eficacia mediante pruebas de estrés controladas para comprobar que el filtrado de logs y el bloqueo a nivel de kernel (`iptables` / `DOCKER-USER`) responden correctamente ante un escenario de ataque de denegación o scraping automatizado.

### 3.1. Simulación de Ataque por Fuerza Bruta / Scraping

Para saturar el límite de peticiones configurado en Nginx (`limit_req`) y forzar la intervención de Fail2ban, puedes lanzar una ráfaga rápida de peticiones HTTP desde una máquina externa (por ejemplo, utilizando un script de bucle o `curl` concurrente):

```bash
seq 1 200 | xargs -P 100 -I{} curl -s -o /dev/null -w "%{http_code}\n" https://moodle.uarn.es/login/test_uuid_falso

```

### 3.2. Comprobación del Estado de la Jaula en Fail2ban

Para verificar si el analizador de logs ha detectado los reintentos fallidos y ha aplicado la directiva de baneo sobre la IP del atacante, ejecuta:

```bash
sudo fail2ban-client status nginx-ratelimit

```

*Este comando mostrará el número total de fallos registrados, el archivo de logs monitorizado y la lista exacta de direcciones IP actualmente bloqueadas.*

### 3.3. Auditoría Directa de las Reglas en el Kernel (iptables)

Dado que el bloqueo se aplica directamente sobre la cadena de reenvío de Docker, puedes inspeccionar el estado del cortafuegos y comprobar que la regla `DROP` se encuentra insertada de forma prioritaria en la primera posición (`-I DOCKER-USER 1`):

```bash
sudo iptables -L DOCKER-USER -v -n --line-numbers

```

*En la salida de este comando deberás observar la regla de salto o descarte asociada a la IP infractora.*

### 3.4. Verificación del Bloqueo Efectivo (Test de Conectividad)

Para comprobar que el kernel está descartando el tráfico antes de que llegue a los contenedores, intenta realizar una petición contra el servidor desde la IP baneada:

```bash
curl -v https://moodle.uarn.es/login/

```

*Si el sistema de defensa opera correctamente, la conexión se quedará congelada en estado de espera (`Trying <IP>:443...`) hasta expirar por tiempo de persistencia (`Timeout`), evidenciando que el cortafuegos ha anulado la comunicación a nivel de capa de red.*

### 3.5. Gestión Manual: Indulto (Unban) de Direcciones IP

Si durante las pruebas experimentales necesitas retirar el baneo a una dirección IP de forma anticipada sin esperar a que transcurra el tiempo de expiración (`bantime`), utiliza el cliente de administración:

```bash
sudo fail2ban-client set nginx-ratelimit unbanip <DIRECCION_IP>

```