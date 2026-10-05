from PIL import Image
import glob, os, sys

# ============================================================
# Montaje de pegatinas de BAÑOS en hojas TownStix 8 por hoja
# (etiqueta 105 x 74,25 mm apaisada, 2 columnas x 4 filas en A4)
# UNA HOJA POR FACULTAD, 8 pegatinas identicas cada una.
# La pegatina vertical se APLANA sobre blanco, se GIRA a
# horizontal (como el diseno original) y se centra en su casilla.
# ============================================================

DPI = 300
def mm2px(mm): return round(mm / 25.4 * DPI)

A4_W, A4_H = mm2px(210), mm2px(297)
DESPLAZO_X = 5   # mm a mover a la IZQUIERDA (sube el número si hace falta más)
COLS_CX  = [mm2px(60 - DESPLAZO_X), mm2px(164 - DESPLAZO_X)] # centro X de columnas
FILAS_CY = [mm2px(36.6), mm2px(111.7), mm2px(184.9), mm2px(258.4)] # centro Y de filas
ANCHO_MAX = mm2px(103)   # la pegatina apaisada se escala a este ancho

CARPETA_PEGATINAS = "pegatinas_banos"
CARPETA_SALIDA    = "pegatinas_banos/HOJAS_TOWNSTIX"

def aplanar_blanco(img):
    if img.mode in ("RGBA", "LA"):
        fondo = Image.new("RGB", img.size, "white")
        fondo.paste(img, mask=img.split()[-1])
        return fondo
    return img.convert("RGB")

def montar_hoja_identica(pegatina_path):
    original = aplanar_blanco(Image.open(pegatina_path))
    girada = original.rotate(-90, expand=True)      # tumbar a horizontal
    escala = ANCHO_MAX / girada.width
    peg = girada.resize((round(girada.width*escala), round(girada.height*escala)), Image.LANCZOS)

    hoja = Image.new("RGB", (A4_W, A4_H), "white")
    for cy in FILAS_CY:
        for cx in COLS_CX:
            hoja.paste(peg, (cx - peg.width//2, cy - peg.height//2))
    return hoja

def main():
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    archivos = sorted(glob.glob(os.path.join(CARPETA_PEGATINAS, "pegatina_banos_*.png")))
    if not archivos:
        print(f"No hay pegatinas en {CARPETA_PEGATINAS}/ (pegatina_banos_<facultad>.png)")
        sys.exit(1)
    print(f"Generando {len(archivos)} hojas de banos...")
    for f in archivos:
        slug = os.path.basename(f).replace("pegatina_banos_", "").replace(".png", "")
        hoja = montar_hoja_identica(f)
        salida = os.path.join(CARPETA_SALIDA, f"HOJA_banos_{slug}.pdf")
        hoja.save(salida, "PDF", resolution=DPI)
        print(f"  OK {slug:12} -> {os.path.basename(salida)} (8 pegatinas)")
    print(f"\nHojas en {CARPETA_SALIDA}/")
    print(f"Verifica: for f in {CARPETA_SALIDA}/*.pdf; do python3 verificar_qrs.py \"$f\" --esperados 8; done")

if __name__ == "__main__":
    main()