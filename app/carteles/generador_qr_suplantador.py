from PIL import Image, ImageDraw, ImageFont, ImageOps
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
    ("doctorado",  "Escuela de Doctorado"),
]

def generar_suplantador(qr_path, output_path, nombre_facultad):
    if not os.path.exists(qr_path):
        print(f"❌ No se encuentra el QR '{qr_path}'")
        return

    try:
        # Abrimos el QR y lo convertimos a escala de grises para detectar los límites negros
        qr_raw = Image.open(qr_path).convert("L")
        
        # Invertimos para recortar cualquier margen blanco exterior que traiga el QR original
        qr_inv = ImageOps.invert(qr_raw)
        caja_recorte = qr_inv.getbbox()
        
        if caja_recorte:
            qr_recortado = qr_raw.crop(caja_recorte).convert("RGB")
        else:
            qr_recortado = Image.open(qr_path).convert("RGB")

        # Dimensiones compactas y proporcionadas
        lienzo_size = 800
        borde_grosor = 8
        margen = 50  # Margen blanco/gris uniforme en los 4 lados (ajustar si se quiere aún más ceñido)

        lienzo = Image.new('RGB', (lienzo_size, lienzo_size), color=(248, 248, 248))
        draw = ImageDraw.Draw(lienzo)

        # Recuadro perimetral
        draw.rectangle([0, 0, lienzo_size - 1, lienzo_size - 1], outline=(40, 40, 40), width=borde_grosor)

        # Redimensionamos el QR al espacio interior disponible
        qr_target_size = lienzo_size - (2 * margen)
        qr_img = qr_recortado.resize((qr_target_size, qr_target_size), Image.Resampling.LANCZOS)

        # Pegado centrado simétricamente
        lienzo.paste(qr_img, (margen, margen))

        lienzo.save(output_path, "PNG")
        print(f"✅ {nombre_facultad} → {output_path}")

    except Exception as e:
        print(f"❌ Error en {nombre_facultad}: {e}")

if __name__ == "__main__":
    print("🚀 Generando pegatinas suplantadoras ajustadas...")

    for slug, nombre in FACULTADES_SUPLANTADORES:
        qr_path     = f"../qrs_campana/qr_{slug}_suplantadores.png"
        output_path = os.path.join(output_folder, f"pegatina_suplantador_{slug}.png")
        generar_suplantador(qr_path, output_path, nombre)

    print("\n✅ ¡Pegatinas suplantadoras generadas en /pegatinas_suplantadores/!")