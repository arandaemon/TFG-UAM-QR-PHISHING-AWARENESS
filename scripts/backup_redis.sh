#!/usr/bin/env bash
# ============================================================
# backup_redis.sh — Copia de seguridad de la BD Redis del TFG
# Fuerza un guardado y copia TODO el directorio de datos de
# Redis (RDB + AOF) comprimido con fecha. Rota las copias viejas.
# Pensado para correr por cron cada pocas horas.
# ============================================================
set -euo pipefail

# --- CONFIG ---
PROYECTO_DIR="/home/seif/tfg-qr-phishing"      # donde está el docker-compose.yml
SERVICIO_REDIS="redis"                          # nombre del SERVICIO en docker-compose.yml
DATA_DIR="$PROYECTO_DIR/redis_data"             # volumen de datos de Redis en el host
BACKUP_DIR="/home/seif/backups_redis"           # dónde se guardan las copias
RETENER=48                                      # nº de copias a conservar (48 = 6 días si corre cada 3h)

# --- No tocar de aquí abajo ---
mkdir -p "$BACKUP_DIR"
cd "$PROYECTO_DIR"

FECHA=$(date +%Y%m%d_%H%M%S)
DESTINO="$BACKUP_DIR/redis_${FECHA}.tar.gz"

# 1) Fuerza un guardado síncrono para que el RDB en disco esté al día.
#    (El AOF ya se escribe en tiempo real, pero esto asegura consistencia.)
echo "[$(date)] Lanzando SAVE en Redis..."
docker compose exec -T "$SERVICIO_REDIS" redis-cli SAVE

# 2) Comprime TODO el directorio de datos (RDB + appendonlydir)
if [ ! -d "$DATA_DIR" ]; then
    echo "ERROR: no existe $DATA_DIR" >&2
    exit 1
fi
tar -czf "$DESTINO" -C "$PROYECTO_DIR" "$(basename "$DATA_DIR")"
echo "[$(date)] Copia guardada: $DESTINO ($(du -h "$DESTINO" | cut -f1))"

# 3) Rotación: conserva solo las $RETENER más recientes
ls -1t "$BACKUP_DIR"/redis_*.tar.gz 2>/dev/null | tail -n +$((RETENER + 1)) | xargs -r rm -f
echo "[$(date)] Rotación hecha (conservando $RETENER copias)."
