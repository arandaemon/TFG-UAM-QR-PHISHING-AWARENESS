from pypdf import PdfWriter
import glob, os

# ============================================================
# Fusiona las hojas de pegatinas en un unico PDF por tipo:
#   - SUPLANTADORES_TODOS.pdf  (9 hojas, una por facultad)
#   - BANOS_TODOS.pdf          (9 hojas, una por facultad)
# Para mandar a imprenta comodo, como los carteles por facultad.
# ============================================================

TRABAJOS = [
    ("SUPLANTADORES", "pegatinas_suplantadores/HOJAS_L7121",     "HOJA_suplantador_*.pdf"),
    ("BANOS",         "pegatinas_banos/HOJAS_TOWNSTIX",          "HOJA_banos_*.pdf"),
]

SALIDA_DIR = "pegatinas_fusionadas"
os.makedirs(SALIDA_DIR, exist_ok=True)

for nombre, carpeta, patron in TRABAJOS:
    rutas = sorted(glob.glob(os.path.join(carpeta, patron)))
    if not rutas:
        print(f"  (sin hojas en {carpeta}, salto {nombre})")
        continue
    writer = PdfWriter()
    for r in rutas:
        writer.append(r)
    salida = os.path.join(SALIDA_DIR, f"{nombre}_TODOS.pdf")
    with open(salida, "wb") as f:
        writer.write(f)
    writer.close()
    print(f"  OK {nombre}: {len(rutas)} hojas -> {salida}")

print(f"\nFusionados en {SALIDA_DIR}/")