#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 test_defensas.py  —  Pruebas end-to-end de las defensas del TFG (SEIF/UAM)
==============================================================================

Ataca al servidor como lo haría un atacante (mismo flujo que exploit.py) y
verifica, contra el panel de administración, que cada defensa se comporta como
esperamos. Objetivo: no llevarnos sorpresas el día del despliegue.

⚠️  BORRA LA BASE DE DATOS varias veces (usa /reset-db). NO lo ejecutes contra
    el servidor de producción con datos reales de la campaña. Úsalo contra una
    instancia de PRUEBAS. Por seguridad exige el flag  --si  (o PRUEBAS_OK=1).

------------------------------------------------------------------------------
CÓMO EJECUTARLO (recomendado: dentro del contenedor, saltándose Nginx para que
el rate-limit del proxy no interfiera):

    docker cp test_defensas.py flask_backend:/app/test_defensas.py
    docker exec -it flask_backend python /app/test_defensas.py --si

    (dentro del contenedor localhost:8000 es Flask directo, y ADMIN_USER/PASS/
     PATH ya están en el entorno vía .env)

O desde tu máquina contra una instancia de pruebas con el puerto 8000 expuesto:

    BASE_URL=http://localhost:8000 ADMIN_USER=... ADMIN_PASS=... \
    ADMIN_PATH=... python3 test_defensas.py --si

------------------------------------------------------------------------------
Nota: el rate-limit de Nginx (5r/m en /validar) y Fail2ban son otra capa; se
prueban aparte con stress-test.sh. Este script prueba la lógica de la APP.
==============================================================================
"""

import os
import re
import sys
import time
import requests

# --------------------------------------------------------------------------
# Configuración (por variables de entorno, con valores por defecto sensatos)
# --------------------------------------------------------------------------
BASE       = os.environ.get("BASE_URL", "http://localhost:8000").rstrip("/")
ADMIN_USER = os.environ.get("ADMIN_USER", "")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "")
ADMIN_PATH = os.environ.get("ADMIN_PATH", "admin-default").strip("/")
VERIFY     = os.environ.get("TLS_VERIFY", "true").lower() != "false"
FRASE_BORRADO = "BORRAR DATOS DEL TFG"

# Dos QR reales de rutas_qrs.py, MISMA facultad, ubicaciones DISTINTAS
UUID_A = os.environ.get("UUID_A", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")  # Ciencias / Cafetería
UUID_B = os.environ.get("UUID_B", "5d5b09f6d32c4a92964177d018ccbe25032a2e2b9508bc50d27db127027aeb9e")  # Ciencias / Biblioteca

# Marcador estable de la página de concienciación (respuesta única)
MARCADOR_CONCIENCIACION = "ataque de Phishing"

if not VERIFY:
    try:
        requests.packages.urllib3.disable_warnings()  # type: ignore
    except Exception:
        pass

# --------------------------------------------------------------------------
# Utilidades de salida
# --------------------------------------------------------------------------
V, R, Y, C, X = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[0m"
_res = {"ok": 0, "fail": 0}

def check(nombre, condicion, detalle=""):
    estado = f"{V}PASS{X}" if condicion else f"{R}FALL{X}"
    _res["ok" if condicion else "fail"] += 1
    print(f"  [{estado}] {nombre}" + (f"  — {detalle}" if detalle else ""))
    return condicion

def titulo(t):
    print(f"\n{C}== {t} =={X}")

# --------------------------------------------------------------------------
# Cliente del flujo de phishing (idéntico a como lo haría un bot)
# --------------------------------------------------------------------------
def _permitir_cookie_http(s):
    # En PRUEBAS por HTTP la app marca la cookie de sesión como Secure
    # (SESSION_COOKIE_SECURE=True, correcto en producción HTTPS). requests no
    # la reenvía sobre http://, así que le quitamos el flag Secure SOLO en el
    # test para poder mantener la sesión. No toca la app.
    for c in s.cookies:
        c.secure = False

def flujo(username, *, con_token=True, csrf_ok=True, honeypot=False,
          esperar=1.3, uuid=UUID_A):
    """Hace el flujo completo con una sesión NUEVA y devuelve (sesion, respuesta)."""
    s = requests.Session()
    # 1) Escanea el QR (fija centro en sesión). Sin seguir la redirección para
    #    poder desactivar el flag Secure de la cookie antes del siguiente paso.
    s.get(f"{BASE}/login/{uuid}", verify=VERIFY, timeout=15, allow_redirects=False)
    _permitir_cookie_http(s)
    # 2) Carga index.php (ya con la sesión) y extrae csrf_token + token
    r = s.get(f"{BASE}/login/index.php", verify=VERIFY, timeout=15)
    _permitir_cookie_http(s)
    m_csrf = re.search(r'name="csrf_token" value="([^"]+)"', r.text)
    m_tok  = re.search(r"getElementById\('tok_field'\)\.value = \"([^\"]+)\"", r.text)
    csrf = m_csrf.group(1) if m_csrf else ""
    tok  = m_tok.group(1) if m_tok else ""
    # 3) Construye el formulario (con las trampas activadas según parámetros)
    data = {"username": username, "csrf_token": csrf if csrf_ok else "csrf-falso"}
    if con_token:
        data["token_form"] = tok
    if honeypot:
        data["website"] = "http://bot-spam.example"
    if esperar:
        time.sleep(esperar)
    r2 = s.post(f"{BASE}/validar", data=data, verify=VERIFY, timeout=15)
    return s, r2

# --------------------------------------------------------------------------
# Lectura de métricas desde el CSV del panel de administración
# --------------------------------------------------------------------------
def leer_metricas():
    r = requests.get(f"{BASE}/{ADMIN_PATH}/csv", auth=(ADMIN_USER, ADMIN_PASS),
                     verify=VERIFY, timeout=20)
    r.raise_for_status()
    limpios = apartados = victimas_unicas = 0
    impactos_total = 0
    seccion = None
    for ln in r.text.splitlines():
        if ln.startswith("---"):
            seccion = ln.strip("- ").strip()
            continue
        if not ln.strip():
            seccion = None
            continue
        # Víctimas únicas globales = embudo fase 3 (dedup por email a nivel global)
        if seccion and seccion.startswith("EMBUDO DE CONVERSION GLOBAL"):
            if ln.startswith('"3_password"'):
                try: victimas_unicas = int(ln.split(",")[1])
                except (ValueError, IndexError): pass
        # Resumen de cuarentena (contadores de eventos)
        if seccion and seccion.startswith("RESUMEN DE CUARENTENA"):
            if ln.startswith('"Impactos limpios'):
                limpios = int(ln.rsplit(",", 1)[1])
            elif ln.startswith('"Envios apartados'):
                apartados = int(ln.rsplit(",", 1)[1])
        # Impactos por ubicación (SCARD por centro:ubicación) = impactos ÚNICOS reales
        if seccion and seccion.startswith("IMPACTOS POR UBICAC"):
            partes = ln.split(",")
            if ln.startswith('"') and partes[-1].strip().isdigit():
                impactos_total += int(partes[-1])
    return {"limpios": limpios, "apartados": apartados,
            "impactos": impactos_total, "victimas_unicas": victimas_unicas}

def reset(confirmacion=FRASE_BORRADO):
    return requests.post(f"{BASE}/{ADMIN_PATH}/reset-db", auth=(ADMIN_USER, ADMIN_PASS),
                         data={"confirmacion": confirmacion}, verify=VERIFY, timeout=20)

# --------------------------------------------------------------------------
# ESCENARIOS
# --------------------------------------------------------------------------
def escenarios():
    ALUMNO = "alumno1@estudiante.uam.es"

    # --- S1: humano legítimo -> DEBE CONTAR ---
    titulo("S1 · Humano legítimo (email UAM, token OK, sin trampas, espera > umbral)")
    reset()
    flujo(ALUMNO, esperar=1.3)
    m = leer_metricas()
    check("El impacto se cuenta (1)", m["impactos"] == 1, f"impactos={m['impactos']}")
    check("No queda en cuarentena", m["apartados"] == 0, f"apartados={m['apartados']}")

    # --- S2: dedup por email (mismo correo, misma ubicación, x5) -> 1 impacto ---
    titulo("S2 · Dedup por email: mismo correo 5 veces (sesiones nuevas) = 1 impacto")
    reset()
    for _ in range(5):
        flujo(ALUMNO, esperar=1.2)
    m = leer_metricas()
    check("100→1: 5 envíos del mismo correo = 1 impacto", m["impactos"] == 1,
          f"impactos={m['impactos']} (limpios/eventos={m['limpios']})")

    # --- S3: correos distintos -> N impactos ---
    titulo("S3 · Correos distintos: 3 alumnos = 3 impactos")
    reset()
    for i in range(3):
        flujo(f"alumno{i}@estudiante.uam.es", esperar=1.2)
    m = leer_metricas()
    check("3 correos distintos = 3 impactos", m["impactos"] == 3, f"impactos={m['impactos']}")

    # --- S4: mismo correo, dos QR distintos -> 2 por ubicación, 1 víctima única ---
    titulo("S4 · Mismo correo en 2 QR distintos: 2 impactos por ubicación, 1 víctima única")
    reset()
    flujo(ALUMNO, esperar=1.2, uuid=UUID_A)
    flujo(ALUMNO, esperar=1.2, uuid=UUID_B)
    m = leer_metricas()
    check("Suma por ubicación = 2", m["impactos"] == 2, f"impactos={m['impactos']}")
    check("Víctimas únicas globales = 1", m["victimas_unicas"] == 1, f"unicas={m['victimas_unicas']}")

    # --- S5: honeypot (señal FUERTE) -> cuarentena ---
    titulo("S5 · Honeypot relleno (señal fuerte) → cuarentena, NO cuenta")
    reset()
    flujo(ALUMNO, esperar=1.2, honeypot=True)
    m = leer_metricas()
    check("No cuenta como impacto", m["impactos"] == 0, f"impactos={m['impactos']}")
    check("Queda apartado (1)", m["apartados"] == 1, f"apartados={m['apartados']}")

    # --- S6: sin token anti-envenenamiento (señal FUERTE) -> cuarentena ---
    titulo("S6 · Sin token_form (señal fuerte) → cuarentena, NO cuenta")
    reset()
    flujo(ALUMNO, esperar=1.2, con_token=False)
    m = leer_metricas()
    check("No cuenta como impacto", m["impactos"] == 0, f"impactos={m['impactos']}")
    check("Queda apartado (1)", m["apartados"] == 1, f"apartados={m['apartados']}")

    # --- S7: doble envío en la MISMA sesión -> el 2º da 404 (centro consumido) ---
    titulo("S7 · Doble envío en la misma sesión → el 2º intento es 404")
    reset()
    s, r1 = flujo(ALUMNO, esperar=1.2)
    r2 = s.post(f"{BASE}/validar", data={"username": ALUMNO}, verify=VERIFY, timeout=15)
    check("El 2º envío de la misma sesión se rechaza (404)", r2.status_code == 404,
          f"status={r2.status_code}")

    # --- S8: una sola señal DÉBIL (csrf) con email válido -> SÍ cuenta (por diseño) ---
    titulo("S8 · Una señal débil sola (csrf malo, email válido) → SÍ cuenta")
    reset()
    flujo(ALUMNO, esperar=1.2, csrf_ok=False)   # 1 señal débil ('csrf')
    m = leer_metricas()
    check("1 señal débil sola NO aparta (cuenta)", m["impactos"] == 1,
          f"impactos={m['impactos']} — débiles (tiempo/csrf/ip) solas cuentan; 2+ apartan")

    # --- S9: dos señales débiles (csrf + email no-UAM) -> cuarentena ---
    titulo("S9 · Dos señales débiles (csrf malo + email no-UAM) → cuarentena, NO cuenta")
    reset()
    flujo("hacker@gmail.com", esperar=1.2, csrf_ok=False)  # 'csrf' + 'email_invalido' = 2 débiles
    m = leer_metricas()
    check("2 señales débiles apartan", m["impactos"] == 0, f"impactos={m['impactos']}")
    check("Queda apartado (1)", m["apartados"] == 1, f"apartados={m['apartados']}")

    # --- S10: email fuera del dominio UAM -> NO cuenta como impacto ---
    titulo("S10 · Email no-UAM (gmail) → NO cuenta como impacto")
    reset()
    flujo("hacker@gmail.com", esperar=1.2)
    m = leer_metricas()
    check("Correo no-UAM no suma impacto", m["impactos"] == 0, f"impactos={m['impactos']}")

    # --- S11: respuesta ÚNICA (sin oráculo) ---
    titulo("S11 · Respuesta única: limpio y apartado devuelven la MISMA página")
    reset()
    _, r_ok  = flujo(ALUMNO, esperar=1.2)                 # cuenta
    _, r_bad = flujo(ALUMNO, esperar=1.2, honeypot=True)  # apartado
    ok_marca  = MARCADOR_CONCIENCIACION in r_ok.text
    bad_marca = MARCADOR_CONCIENCIACION in r_bad.text
    check("El limpio ve concienciación", ok_marca)
    check("El apartado ve la MISMA página (no hay oráculo)", bad_marca and r_ok.status_code == r_bad.status_code,
          f"status ok={r_ok.status_code} bad={r_bad.status_code}")

    # --- S12: la contraseña NO se transmite (campo sin name) ---
    titulo("S12 · Ética/RGPD: el campo de contraseña no viaja (sin atributo name)")
    s = requests.Session()
    s.get(f"{BASE}/login/{UUID_A}", verify=VERIFY, timeout=15, allow_redirects=False)
    _permitir_cookie_http(s)
    html = s.get(f"{BASE}/login/index.php", verify=VERIFY, timeout=15).text
    tiene_input_pass = 'type="password"' in html
    tiene_name_pass = 'name="password"' in html
    check("Se muestra el campo contraseña (realismo)", tiene_input_pass)
    check("La contraseña NO tiene name (no se envía)", not tiene_name_pass)

    # --- S13: path traversal ---
    titulo("S13 · Path traversal en /login/<uuid> → 400")
    r = requests.get(f"{BASE}/login/test..test", verify=VERIFY, timeout=15)
    check("Bloquea '..' en el uuid (400)", r.status_code == 400, f"status={r.status_code}")

    # --- S14: el panel de admin exige autenticación ---
    titulo("S14 · El panel de administración exige Basic Auth")
    r = requests.get(f"{BASE}/{ADMIN_PATH}", verify=VERIFY, timeout=15)
    check("Sin credenciales → 401", r.status_code == 401, f"status={r.status_code}")

    # --- S15: confirmación de borrado tipo GitHub ---
    titulo("S15 · Borrado exige la frase exacta (validación en servidor)")
    reset()
    flujo(ALUMNO, esperar=1.2)                       # deja 1 impacto
    reset(confirmacion="cualquier cosa")             # frase incorrecta → NO debe borrar
    m = leer_metricas()
    check("Frase incorrecta NO borra los datos", m["impactos"] == 1, f"impactos={m['impactos']}")
    reset(confirmacion=FRASE_BORRADO)                # frase correcta → borra
    m = leer_metricas()
    check("Frase correcta SÍ borra los datos", m["impactos"] == 0, f"impactos={m['impactos']}")

# --------------------------------------------------------------------------
def main():
    if "--si" not in sys.argv and os.environ.get("PRUEBAS_OK") != "1":
        print(f"{Y}Este script BORRA la base de datos varias veces.{X}")
        print("Ejecútalo SOLO contra una instancia de pruebas, con  --si  (o PRUEBAS_OK=1).")
        sys.exit(2)
    if not ADMIN_USER or not ADMIN_PASS:
        print(f"{R}Faltan ADMIN_USER / ADMIN_PASS en el entorno.{X}")
        sys.exit(2)

    print(f"{C}Objetivo:{X} {BASE}   {C}admin:{X} /{ADMIN_PATH}   {C}TLS verify:{X} {VERIFY}")
    try:
        leer_metricas()  # comprobación de conectividad + credenciales admin
    except Exception as e:
        print(f"{R}No puedo leer el panel ({e}). ¿BASE_URL/credenciales/instancia arriba?{X}")
        sys.exit(2)

    try:
        escenarios()
    finally:
        reset()  # dejamos la BD limpia al terminar

    print(f"\n{C}==================== RESUMEN ===================={X}")
    print(f"  {V}PASS: {_res['ok']}{X}    {R}FALL: {_res['fail']}{X}")
    if _res["fail"] == 0:
        print(f"  {V}✔ Todas las defensas se comportan como esperamos.{X}")
    else:
        print(f"  {R}✗ Hay comprobaciones que fallan: revísalas antes de desplegar.{X}")
    sys.exit(1 if _res["fail"] else 0)

if __name__ == "__main__":
    main()
