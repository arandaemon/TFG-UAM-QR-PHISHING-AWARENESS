from PIL import Image
import os

imagen_base_path = "pegatina_jhon_lenon.png"
output_folder = "pegatinas_banos"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Alineado con los nuevos QRs por facultad
FACULTADES_BANOS = [
    ("ciencias",   "Facultad de Ciencias"),
    ("economicas", "Facultad de Económicas"),
    ("derecho",    "Facultad de Derecho"),
    ("filosofia",  "Facultad de Filosofía y Letras"),
    ("educacion",  "Formación de Profesorado"),
    ("medicina",   "Facultad de Medicina"),
    ("psicologia", "Facultad de Psicología"),
    ("eps",        "Escuela Politécnica Superior"),
    ("doctorado",  "Escuela de Doctorado"),
]

def generar_pegatina_banos(base_path, qr_path, output_path, nombre_facultad):
    if not os.path.exists(base_path):
        print(f"❌ No se encuentra la imagen base '{base_path}'")
        return
    if not os.path.exists(qr_path):
        print(f"❌ No se encuentra el QR '{qr_path}'")
        return

    try:
        # Cargamos en RGBA para preservar el canal alfa si la base tiene recorte
        base = Image.open(base_path).convert("RGBA")
        qr   = Image.open(qr_path).convert("RGBA")

        # Coordenadas ajustadas:
        # Se baja el centro en Y para despejar la boca y ubicarlo en la lengua.
        center_x = 444
        center_y = 818  # Subido de 830 a 818 (no tapa los dientes y no se sale por la barba)
        size_qr  = 210  # Ajustado de 220 a 205 para que mantenga su marco blanco dentro de la silueta

        # Redimensionado de alta calidad para preservar bordes nítidos
        qr_resized = qr.resize((size_qr, size_qr), Image.Resampling.LANCZOS)
        
        paste_x = center_x - (size_qr // 2)
        paste_y = center_y - (size_qr // 2)

        # Pegamos el QR utilizando su propia máscara si la tuviera
        base.paste(qr_resized, (paste_x, paste_y), qr_resized)

        # Guardamos forzando 300 DPI para la imprenta
        base.save(output_path, "PNG", dpi=(300, 300))
        print(f"✅ {nombre_facultad} → {output_path}")

    except Exception as e:
        print(f"❌ Error en {nombre_facultad}: {e}")

if __name__ == "__main__":
    print("🚀 Generando pegatinas de baños por facultad...")

    if not os.path.exists(imagen_base_path):
        print(f"❌ Falta la imagen base '{imagen_base_path}'")
    else:
        for slug, nombre in FACULTADES_BANOS:
            qr_path     = f"../qrs_campana/qr_{slug}_banos.png"
            output_path = os.path.join(output_folder, f"pegatina_banos_{slug}.png")
            generar_pegatina_banos(imagen_base_path, qr_path, output_path, nombre)

    print("\n✅ ¡Pegatinas de baños generadas en /pegatinas_banos/!")