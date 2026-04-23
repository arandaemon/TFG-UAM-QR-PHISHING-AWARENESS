from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIGURACIÓN TÁCTICA ---
qr_crudo_path = "../qrs_campana/qr_uam_suplantadores.png"
pegatina_final_path = "pegatina_suplantador_final.png"

def forjar_suplantador(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"❌ Error: No encuentro el QR en '{input_path}'")
        return

    try:
        lienzo_size = 800
        bg_color = (248, 248, 248) 
        lienzo = Image.new('RGB', (lienzo_size, lienzo_size), color=bg_color)
        draw = ImageDraw.Draw(lienzo)

        # Borde
        grosor_borde = 8
        draw.rectangle([0, 0, lienzo_size, lienzo_size], outline=(40,40,40), width=grosor_borde)

        # Cargar QR 4
        qr_img = Image.open(input_path).convert("RGB")
        qr_size = 550 
        qr_resized = qr_img.resize((qr_size, qr_size))

        # Posicionamos el QR arriba
        paste_x = (lienzo_size - qr_size) // 2
        paste_y = 50 
        lienzo.paste(qr_resized, (paste_x, paste_y))

        # CARGA DE FUENTE ROBUSTA
        texto = "ESCANEAR AQUÍ"
        font_size = 85 # Tamaño serio para un lienzo de 800
        
        # Rutas comunes en Ubuntu/Debian
        rutas_fuentes = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "arial.ttf", 
            "FreeSans.ttf"
        ]
        
        font = None
        for ruta in rutas_fuentes:
            try:
                font = ImageFont.truetype(ruta, font_size)
                print(f"✅ Fuente cargada: {ruta}")
                break
            except:
                continue

        if font is None:
            font = ImageFont.load_default()
            print("⚠️ ADVERTENCIA: No se encontró ninguna fuente TrueType. El texto saldrá PEQUEÑO.")

        # Centrar texto
        caja_texto = draw.textbbox((0, 0), texto, font=font)
        ancho_texto = caja_texto[2] - caja_texto[0]
        texto_x = (lienzo_size - ancho_texto) // 2
        texto_y = paste_y + qr_size + 30 # Separación del QR

        draw.text((texto_x, texto_y), texto, fill=(40,40,40), font=font)

        lienzo.save(output_path, "PNG")
        print(f"✅ Pegatina generada: {output_path}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    forjar_suplantador(qr_crudo_path, pegatina_final_path)