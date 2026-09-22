from PIL import Image, ImageDraw, ImageFont
import os

DISEÑOS = {
    "Dumbo":  {"fondo": "cartel_dumbo.png",  "pos": (359, 724),  "size": 405},
    "Menu":   {"fondo": "cartel_menu.png",   "pos": (538, 1407), "size": 336},
    "Becas":  {"fondo": "cartel_becas.png",  "pos": (115, 200),  "size": 650},
    "Wuolah": {"fondo": "cartel_wuolah.png", "pos": (1033, 1639), "size": 281},
    "Mus":    {"fondo": "cartel_mus.png",    "pos": (860, 1510), "size": 348},
    "Mesas":  {"fondo": "cartel_mesas.png",  "pos": (841, 2350), "size": 800}
}

QR_FOLDER = "../qrs_campana"
OUTPUT_FOLDER = "pdfs_finales_imprenta"

nombres_qrs = [
    "global_renfe", "global_bus", "global_plaza",
    "uam_banos", "uam_suplantadores",
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

print("Generando y separando carteles A4 y carteles de mesa A5...")

for nombre_qr in nombres_qrs:
    if nombre_qr in ["uam_banos", "uam_suplantadores"]:
        print(f"{nombre_qr}: Saltando (Pegatina de imprenta).")
        continue 
    
    centro = nombre_qr.split('_')[0].upper()
    qr_path = os.path.join(QR_FOLDER, f"qr_{nombre_qr}.png")
    
    if not os.path.exists(qr_path):
        print(f" No se encontró el QR base: {qr_path}")
        continue

    for nombre_diseno, params in DISEÑOS.items():
        try:
            cartel = Image.open(params["fondo"]).convert("RGB")
            qr = Image.open(qr_path).resize((params["size"], params["size"]))
            cartel.paste(qr, params["pos"])
            
            draw = ImageDraw.Draw(cartel)
            etiqueta_limpia = nombre_qr.replace("_", " ").upper()
            
            try:
                font = ImageFont.truetype("arial.ttf", 35)
            except:
                font = ImageFont.load_default()

            draw.text((50, 50), etiqueta_limpia, fill=(180, 180, 180), font=font)
            
            # --- SEPARACIÓN FORMATO A5 ---
            if nombre_diseno == "Mesas":
                carpeta_destino = os.path.join(OUTPUT_FOLDER, "FORMATO_A5_MESAS", centro)
            else:
                carpeta_destino = os.path.join(OUTPUT_FOLDER, "FORMATO_A4_NORMAL", centro)
                
            if not os.path.exists(carpeta_destino):
                os.makedirs(carpeta_destino)
            
            nombre_salida = os.path.basename(f"PDF_{nombre_qr}_con_{nombre_diseno}.pdf")
            ruta_salida = os.path.join(carpeta_destino, nombre_salida)
            
            cartel.save(ruta_salida, "PDF", resolution=300.0)
            print(f" ✅ Generado: {nombre_salida}")
            
        except Exception as e:
            print(f" ❌ Error en la permutación {nombre_qr} + {nombre_diseno}: {e}")

print(f"\n🚀 Todo organizado por tamaños en '{OUTPUT_FOLDER}'.")