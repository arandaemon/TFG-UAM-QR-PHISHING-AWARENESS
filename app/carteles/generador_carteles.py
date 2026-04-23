from PIL import Image, ImageDraw, ImageFont
import os

# COORDENADAS CORREGIDAS
DISEÑOS = {
    "Dumbo":  {"fondo": "cartel_dumbo.png",  "pos": (359, 724),  "size": 405},
    "Menu":   {"fondo": "cartel_menu.png",   "pos": (538, 1407), "size": 336},
    "Becas":  {"fondo": "cartel_becas.png",  "pos": (117, 141),  "size": 336},
    "Wuolah": {"fondo": "cartel_wuolah.png", "pos": (1033, 1639), "size": 281},
    "Mus":    {"fondo": "cartel_mus.png",    "pos": (860, 1510), "size": 348}
}

QR_FOLDER = "../qrs_campana"
OUTPUT_FOLDER = "pdfs_finales_imprenta"

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Lista de nombres de QRs (Alineada exactamente con las 32 rutas)
nombres_qrs = [
    "global_renfe", "global_bus", "global_plaza",
    "uam_banos", "uam_suplantadores", # Pegatinas globales
    "ciencias_cafeteria", "ciencias_biblioteca", "ciencias_pasillos",
    "economicas_cafeteria", "economicas_biblioteca", "economicas_pasillos",
    "derecho_cafeteria", "derecho_biblioteca", "derecho_pasillos",
    "filosofia_cafeteria", "filosofia_biblioteca", "filosofia_pasillos",
    "educacion_cafeteria", "educacion_biblioteca", "educacion_pasillos",
    "medicina_cafeteria", "medicina_biblioteca", "medicina_pasillos",
    "psicologia_cafeteria", "psicologia_biblioteca", "psicologia_pasillos",
    "eps_cafeteria", "eps_biblioteca", "eps_pasillos",
    "doctorado_cafeteria", "doctorado_biblioteca", "doctorado_pasillos"
]

print("🎨 Generando TODAS las permutaciones organizadas por facultades...")

for nombre_qr in nombres_qrs:
    
    # Saltamos las pegatinas de imprenta
    if nombre_qr in ["uam_banos", "uam_suplantadores"]:
        print(f" ⏩ {nombre_qr}: Saltando (Es pegatina directa para imprenta, no lleva cartel).")
        continue 
    
    # Extraemos la facultad
    centro = nombre_qr.split('_')[0].upper()
    
    # Creamos la subcarpeta de la facultad
    subcarpeta_centro = os.path.join(OUTPUT_FOLDER, centro)
    if not os.path.exists(subcarpeta_centro):
        os.makedirs(subcarpeta_centro)
        
    qr_path = os.path.join(QR_FOLDER, f"qr_{nombre_qr}.png")
    
    if not os.path.exists(qr_path):
        print(f" ⚠️ No se encontró el QR base: {qr_path}")
        continue

    # Por cada ubicación, generamos los 5 diseños
    for nombre_diseno, params in DISEÑOS.items():
        try:
            # Cargamos el fondo específico
            cartel = Image.open(params["fondo"]).convert("RGB")
            
            # Cargamos y redimensionamos QR
            qr = Image.open(qr_path)
            qr = qr.resize((params["size"], params["size"]))
            
            # Pegamos el QR
            cartel.paste(qr, params["pos"])
            
            draw = ImageDraw.Draw(cartel)
            etiqueta_limpia = nombre_qr.replace("_", " ").upper()
            
            try:
                font = ImageFont.truetype("arial.ttf", 35)
            except:
                font = ImageFont.load_default()

            draw.text((50, 50), etiqueta_limpia, fill=(180, 180, 180), font=font)
            
            # Saneamiento de nombre de archivo (Buenas prácticas de seguridad)
            nombre_salida = os.path.basename(f"PDF_{nombre_qr}_con_{nombre_diseno}.pdf")
            ruta_salida = os.path.join(subcarpeta_centro, nombre_salida)
            
            cartel.save(ruta_salida, "PDF", resolution=300.0)
            print(f" ✅ Generado en /{centro}/: {nombre_salida}")
            
        except Exception as e:
            print(f" ❌ Error en la permutación {nombre_qr} + {nombre_diseno}: {e}")

print(f"\n🚀 ¡Todo ordenado! Revisa las subcarpetas dentro de '{OUTPUT_FOLDER}'.")