#!/bin/bash
# =============================================================================
#  test_red.sh — Prueba de la capa de RED: Nginx rate-limit, Fail2ban y NAT
# =============================================================================
#  Mide cuánto tráfico deja pasar Nginx por IP y si Fail2ban banea. Sirve para
#  saber si el NAT de Eduroam (muchos alumnos, una IP) será un problema.
#
#  ⚠️  EJECÚTALO DESDE UNA MÁQUINA EXTERNA (tu portátil, el móvil compartiendo
#      datos, la Kali...), NO desde el servidor: Fail2ban banea por IP de origen
#      y desde el propio servidor verías 127.0.0.1, no un cliente real.
#
#  ⚠️  El Test 3 HARÁ que Fail2ban banee tu IP ~5 min. Ten a mano el unban
#      (al final) o usa una IP/red que puedas permitirte banear.
#
#  Uso:   URL=https://moodle.uarn.es ./test_red.sh
# =============================================================================

URL="${URL:-https://moodle.uarn.es}"
UUID="${UUID:-e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855}"

# -k: ignora validación TLS (por si pruebas con IP/host raro).  -m 4: timeout.
codigo() { curl -s -k -m 4 -o /dev/null -w "%{http_code}" "$@"; }

echo "Objetivo: $URL"
echo "IP saliente (la que verá Nginx/Fail2ban): $(curl -s -m 5 https://api.ipify.org || echo '¿sin salida?')"
echo

# -----------------------------------------------------------------------------
echo "== Test 1 · Ráfaga de ESCANEOS (GET /login) — simula un cambio de clase =="
echo "   Nginx: zone=login_qr 10r/s burst=50. 50 alumnos a la vez deberían pasar."
ok=0; lim=0; ban=0
for i in $(seq 1 60); do
  c=$(codigo "$URL/login/$UUID")
  case "$c" in
    200|302|404) ok=$((ok+1));;
    429)         lim=$((lim+1));;
    000)         ban=$((ban+1));;
  esac
done
echo "   Resultado (de 60):  pasan=$ok   limitados(429)=$lim   cortados(000)=$ban"
echo

sleep 5   # deja que se rellene un poco la ventana

# -----------------------------------------------------------------------------
echo "== Test 2 · Ráfaga de ENVÍOS (POST /validar) — el CUELLO DE BOTELLA del NAT =="
echo "   Nginx: zone=validar 5r/m burst=5. Esto es lo que aguanta UNA IP (=un NAT)."
ok=0; lim=0; ban=0
for i in $(seq 1 30); do
  c=$(codigo -X POST "$URL/validar" --data "x=1")
  case "$c" in
    200|302|403|404) ok=$((ok+1));;   # llegó a Flask (da 404/403 por sesión/csrf, da igual)
    429)             lim=$((lim+1));;
    000)             ban=$((ban+1));;
  esac
done
echo "   Resultado (de 30):  pasan=$ok   limitados(429)=$lim   cortados(000)=$ban"
echo "   → 'pasan' ≈ cuántos ENVÍOS de formulario tolera un NAT en ~1 min."
echo "     Si tu clase más grande por IP supera ese número, habrá alumnos legítimos con 429."
echo

# -----------------------------------------------------------------------------
echo "== Test 3 · Saturación para comprobar FAIL2BAN (⚠️ ESTO TE BANEA ~5 min) =="
echo "   Fail2ban: maxretry=15, findtime=10s. Lanzamos 40 seguidas."
seq=""
for i in $(seq 1 40); do
  c=$(codigo "$URL/login/$UUID")
  seq="$seq $c"
done
echo "   Códigos: $seq"
if echo "$seq" | grep -q "000"; then
  echo "   ✔ Aparecen 000 al final → Fail2ban te ha baneado a nivel de kernel (correcto)."
else
  echo "   ⚠ No hay 000: o Fail2ban no está activo, o no llegaste al umbral. Revisa en el server."
fi
echo

cat <<'AYUDA'
=============================================================================
COMPROBAR / DESHACER EN EL SERVIDOR (donde corre Fail2ban):

  sudo fail2ban-client status nginx-ratelimit         # fallos y IPs baneadas
  sudo iptables -L DOCKER-USER -n --line-numbers       # regla DROP insertada
  sudo fail2ban-client set nginx-ratelimit unbanip <TU_IP>   # quitar el ban

PRUEBA DE CARGA (opcional, necesita 'hey' o 'ab'; TAMBIÉN dispara Fail2ban):
  hey -z 20s -c 20 "URL/login/UUID"
  ab  -n 500 -c 20 "URL/login/UUID"
=============================================================================
AYUDA
