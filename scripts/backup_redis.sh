#!/usr/bin/env bash
set -euo pipefail

PROYECTO_DIR="/home/seif/tfg-qr-phishing"
SERVICIO_REDIS="redis"
BACKUP_DIR="/home/seif/backups_redis"
RETENER=48

mkdir -p "$BACKUP_DIR"
cd "$PROYECTO_DIR"

FECHA=$(date +%Y%m%d_%H%M%S)
DESTINO="$BACKUP_DIR/redis_${FECHA}.tar.gz"

echo "[$(date)] Lanzando SAVE en Redis..."
docker compose exec -T "$SERVICIO_REDIS" redis-cli SAVE

echo "[$(date)] Archivando /data desde el contenedor..."
docker compose exec -T "$SERVICIO_REDIS" tar -czf - -C /data . > "$DESTINO"

if [ ! -s "$DESTINO" ]; then
    echo "ERROR: la copia salió vacía ($DESTINO)" >&2
    rm -f "$DESTINO"
    exit 1
fi
echo "[$(date)] Copia guardada: $DESTINO ($(du -h "$DESTINO" | cut -f1))"

ls -1t "$BACKUP_DIR"/redis_*.tar.gz 2>/dev/null | tail -n +$((RETENER + 1)) | xargs -r rm -f
echo "[$(date)] Rotación hecha (conservando $RETENER copias)."
