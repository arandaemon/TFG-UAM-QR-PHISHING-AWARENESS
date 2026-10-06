from PIL import Image, ImageOps
import os

output_folder = "pegatinas_suplantadores"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

FACULTADES_SUPLANTADORES = [
    ("ciencias",   "Facultad de Ciencias"),
    ("economicas", "Facultad de Económicas"),
    ("derecho",    "Facultad de Derecho"),
    ("filosofia",  "Facultad de Filosofía y Letras"),
    ("educacion",  "Formación de Profesorado"),
    ("medicina",   "Facultad de Medicina"),
    ("psicologia", "Facultad de Psicología"),
    ("eps",        "Escuela Politécnica Superior"),
]

def generar_suplantador(qr_path, output_path, nombre_facultad):
    if not os.path.exists(qr_path):
        print(f"❌ No se encuentra el QR '{qr_path}'")
        return

    try:
        # Abrimos el QR y recortamos a ras absoluto de los módulos negros
        qr_raw = Image.open(qr_path).convert("L")
        qr_inv = ImageOps.invert(qr_raw)
        caja_recorte = qr_inv.getbbox()
        
        if caja_recorte:
            qr_recortado = qr_raw.crop(caja_recorte).convert("RGB")
        else:
            qr_recortado = Image.open(qr_path).convert("RGB")

        tamano_lienzo = 1000
       
        margen = 40  
        qr_target_size = tamano_lienzo - (2 * margen)

        lienzo = Image.new('RGB', (tamano_lienzo, tamano_lienzo), color=(255, 255, 255))
        qr_img = qr_recortado.resize((qr_target_size, qr_target_size), Image.Resampling.LANCZOS)
        lienzo.paste(qr_img, (margen, margen))

        lienzo_final = lienzo.resize((531, 531), Image.LANCZOS)
        lienzo_final.save(output_path, "PNG", dpi=(300, 300))
        print(f"✅ {nombre_facultad} (margen milimétrico 0.75 mm) → {output_path}")

    except Exception as e:
        print(f"❌ Error en {nombre_facultad}: {e}")

if __name__ == "__main__":
    print("🚀 Generando pegatinas con margen microscópico (0.75 mm)...")

    for slug, nombre in FACULTADES_SUPLANTADORES:
        qr_path     = f"../qrs_campana/qr_{slug}_suplantadores.png"
        output_path = os.path.join(output_folder, f"pegatina_suplantador_{slug}.png")
        generar_suplantador(qr_path, output_path, nombre)

    print("\n✅ ¡Listas! Ahora corre de nuevo el script de montaje de hojas Avery.")