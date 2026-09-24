#!/bin/bash

# Cambia esto por tu dominio real o la IP del servidor
URL="https://moodle.uarn.es/login/index.php"

echo "Iniciando ataque de metralleta contra $URL..."
echo "---------------------------------------------------"

# Lanzamos 70 peticiones seguidas para reventar el burst=15 de Nginx
for i in {1..70}; do
    # -s: silencioso, -m 2: timeout de 2 segundos (clave para no quedarse colgado cuando Fail2ban te tire)
    estado=$(curl -s -m 2 -o /dev/null -w "%{http_code}" "$URL")
    
    if [ "$estado" == "000" ]; then
        echo "Intento $i: ☠️ BLOQUEADO (Fail2ban te ha cortado a nivel de firewall)"
    elif [ "$estado" == "503" ]; then
        echo "Intento $i: 🚧 LIMITADO (Nginx te está frenando por rate limit)"
    else
        echo "Intento $i: ✅ HTTP $estado (Nginx procesando petición)"
    fi
done

echo "---------------------------------------------------"
echo "Ataque finalizado."
