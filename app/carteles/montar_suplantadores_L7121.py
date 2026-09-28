from PIL import Image
import glob, os, sys

# ============================================================
# Montaje de pegatinas suplantadoras en hojas Avery L7121
# (45x45 mm, 20 por hoja A4 = 4 columnas x 5 filas)
# UNA HOJA POR FACULTAD, con 20 etiquetas identicas cada una.
# Reparto equitativo: imprimes las hojas que necesites de
# cada facultad por igual.
# Geometria extraida de la plantilla oficial de Avery L7121.
# ============================================================

DPI = 300
def mm2px(mm): return round(mm / 25.4 * DPI)

A4_W, A4_H = mm2px(210), mm2px(297)
ETIQ      = mm2px(45)      # etiqueta 45x45 mm
SEP       = mm2px(5)       # separacion entre etiquetas (H y V)
COLS, FILAS = 4, 5
# Márgenes calculados para CENTRAR la rejilla en el A4 (no los de la plantilla, que van corridos)
_rejilla_w = COLS * ETIQ + (COLS - 1) * SEP
_rejilla_h = FILAS * ETIQ + (FILAS - 1) * SEP
MARG_LEFT = (A4_W - _rejilla_w) // 2
MARG_TOP  = (A4_H - _rejilla_h) // 2
COLS, FILAS = 4, 5         # 20 por hoja

CARPETA_PEGATINAS = "pegatinas_suplantadores"
CARPETA_SALIDA    = "pegatinas_suplantadores/HOJAS_L7121"

def montar_hoja_identica(pegatina_path):
    img = Image.open(pegatina_path).convert("RGB").resize((ETIQ, ETIQ), Image.LANCZOS)
    hoja = Image.new("RGB", (A4_W, A4_H), "white")
    for fila in range(FILAS):
        for col in range(COLS):
            x = MARG_LEFT + col * (ETIQ + SEP)
            y = MARG_TOP  + fila * (ETIQ + SEP)
            hoja.paste(img, (x, y))
    return hoja

def main():
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    archivos = sorted(glob.glob(os.path.join(CARPETA_PEGATINAS, "pegatina_suplantador_*.png")))
    if not archivos:
        print(f"No hay pegatinas en {CARPETA_PEGATINAS}/. Ejecuta antes generador_qr_suplantador.py")
        sys.exit(1)

    print(f"Generando {len(archivos)} hojas (una por facultad, 20 iguales cada una)...")
    for f in archivos:
        slug = os.path.basename(f).replace("pegatina_suplantador_", "").replace(".png", "")
        hoja = montar_hoja_identica(f)
        salida = os.path.join(CARPETA_SALIDA, f"HOJA_suplantador_{slug}.pdf")
        hoja.save(salida, "PDF", resolution=DPI)
        print(f"  OK {slug:12} -> {os.path.basename(salida)} (20 etiquetas)")

    print(f"\nHojas en {CARPETA_SALIDA}/")
    print("Verifica cada una antes de imprimir:")
    print(f"   for f in {CARPETA_SALIDA}/*.pdf; do python3 verificar_qrs.py \"$f\" --esperados 20; done")

if __name__ == "__main__":
    main()