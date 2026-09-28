from PIL import Image, ImageDraw, ImageFont
import os

# Diseños A4 (van a global + cafeteria/biblioteca/pasillos, NO a las mesas)
DISENOS_A4 = {
    "Dumbo":  {"fondo": "cartel_dumbo.png",  "pos": (980, 1760),  "size": 700},
    "Menu":   {"fondo": "cartel_menu.png",   "pos": (1210, 2760), "size": 650},
    "Becas":  {"fondo": "cartel_becas.png",  "pos": (459, 500),   "size": 650},
    "Wuolah": {"fondo": "cartel_wuolah.png", "pos": (2061, 3110), "size": 550},
    "Mus":    {"fondo": "cartel_mus.png",    "pos": (1625, 3000), "size": 650},
}

# Diseño de mesa (va SOLO a los QR _mesa)
DISENO_MESA = {"fondo": "cartel_mesas.png", "pos": (880, 2000), "size": 550}

QR_FOLDER = "../qrs_campana"
OUTPUT_FOLDER = "pdfs_finales_imprenta"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

try:
    FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
except Exception:
    FONT = ImageFont.load_default()

# QR que reciben los 5 diseños A4
qrs_a4 = [
    "global_renfe", "global_bus", "global_plaza",
    "ciencias_cafeteria", "ciencias_biblioteca", "ciencias_pasillos",
    "economicas_cafeteria", "economicas_biblioteca", "economicas_pasillos",
    "derecho_cafeteria", "derecho_biblioteca", "derecho_pasillos",
    "filosofia_cafeteria", "filosofia_biblioteca", "filosofia_pasillos",
    "educacion_cafeteria", "educacion_biblioteca", "educacion_pasillos",
    "medicina_cafeteria", "medicina_biblioteca", "medicina_pasillos",
    "psicologia_cafeteria", "psicologia_biblioteca", "psicologia_pasillos",
    "eps_cafeteria", "eps_biblioteca", "eps_pasillos",
    "doctorado_cafeteria", "doctorado_biblioteca", "doctorado_pasillos",
]

# QR que reciben SOLO el diseño de mesa (uno por centro)
qrs_mesa = [
    "ciencias_mesa", "economicas_mesa", "derecho_mesa", "filosofia_mesa",
    "educacion_mesa", "medicina_mesa", "psicologia_mesa", "eps_mesa",
    "doctorado_mesa",
]

def cargar_qr(nombre_qr, size):
    qr_path = os.path.join(QR_FOLDER, f"qr_{nombre_qr}.png")
    if not os.path.exists(qr_path):
        print(f" ⚠️  No se encontró el QR: {qr_path}")
        return None
    # LANCZOS al reducir mantiene la rejilla del QR uniforme (NEAREST la rompe)
    return Image.open(qr_path).resize((size, size), Image.LANCZOS)

def componer(nombre_qr, nombre_diseno, params, carpeta_destino):
    try:
        cartel = Image.open(params["fondo"]).convert("RGB")
        qr = cargar_qr(nombre_qr, params["size"])
        if qr is None:
            return

        cx, cy = params["pos"]
        top_left = (cx - params["size"] // 2, cy - params["size"] // 2)
        cartel.paste(qr, top_left)

        os.makedirs(carpeta_destino, exist_ok=True)
        nombre_salida = f"PDF_{nombre_qr}_con_{nombre_diseno}.pdf"
        ruta_salida = os.path.join(carpeta_destino, nombre_salida)
        cartel.save(ruta_salida, "PDF", resolution=300.0)
        print(f" ✅ {nombre_salida}")
    except Exception as e:
        print(f" ❌ Error en {nombre_qr} + {nombre_diseno}: {e}")

print("Generando carteles A4 (por facultad) y mesas A5...")

# --- A4: cada QR recibe los 5 diseños ---
for nombre_qr in qrs_a4:
    centro = nombre_qr.split('_')[0].upper()
    for nombre_diseno, params in DISENOS_A4.items():
        destino = os.path.join(OUTPUT_FOLDER, "FORMATO_A4_NORMAL", centro)
        componer(nombre_qr, nombre_diseno, params, destino)

# --- Mesas: cada QR de mesa recibe solo el diseño Mesas ---
for nombre_qr in qrs_mesa:
    destino = os.path.join(OUTPUT_FOLDER, "FORMATO_A5_MESAS")
    componer(nombre_qr, "Mesas", DISENO_MESA, destino)

print(f"\n🚀 Todo organizado en '{OUTPUT_FOLDER}'.")