#!/usr/bin/env bash
# ============================================================
# backup_redis.sh — Copia de seguridad de la BD Redis del TFG
# Fuerza un guardado y archiva TODO el directorio de datos de
# Redis (RDB + AOF) DESDE DENTRO del contenedor (para evitar
# problemas de permisos del volumen en el host), comprimido y
# con fecha. Rota las copias viejas. Pensado para cron.
# ============================================================
set -euo pipefail

# --- CONFIG ---
PROYECTO_DIR="/home/seif/tfg-qr-phishing"      # donde está el docker-compose.yml
SERVICIO_REDIS="redis"                          # nombre del SERVICIO en docker-compose.yml
BACKUP_DIR="/home/seif/backups_redis"           # dónde se guardan las copias
RETENER=48                                      # nº de copias a conservar (48 = 6 días si corre cada 3h)

# --- No tocar de aquí abajo ---
mkdir -p "$BACKUP_DIR"
cd "$PROYECTO_DIR"

FECHA=$(date +%Y%m%d_%H%M%S)
DESTINO="$BACKUP_DIR/redis_${FECHA}.tar.gz"

# 1) Fuerza un guardado síncrono para que el RDB en disco esté al día.
#    (El AOF ya se escribe en tiempo real; esto asegura consistencia.)
echo "[$(date)] Lanzando SAVE en Redis..."
docker compose exec -T "$SERVICIO_REDIS" redis-cli SAVE

# 2) Archiva /data DESDE DENTRO del contenedor (el usuario redis sí puede
#    leer sus propios ficheros) y vuelca el tar.gz directamente al host.
echo "[$(date)] Archivando /data desde el contenedor..."
docker compose exec -T "$SERVICIO_REDIS" tar -czf - -C /data . > "$DESTINO"

# Verificación mínima: que el archivo existe y no está vacío
if [ ! -s "$DESTINO" ]; then
    echo "ERROR: la copia salió vacía ($DESTINO)" >&2
    rm -f "$DESTINO"
    exit 1
fi
echo "[$(date)] Copia guardada: $DESTINO ($(du -h "$DESTINO" | cut -f1))"

# 3) Rotación: conserva solo las $RETENER más recientes
ls -1t "$BACKUP_DIR"/redis_*.tar.gz 2>/dev/null | tail -n +$((RETENER + 1)) | xargs -r rm -f
echo "[$(date)] Rotación hecha (conservando $RETENER copias)."