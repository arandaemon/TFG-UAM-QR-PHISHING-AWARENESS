from PIL import Image
import os

# --- CONFIGURACIÓN ---
imagen_base_path = "pegatina_jhon_lenon.png"
# Apuntamos directamente al nodo global de baños que creamos antes
qr_ejemplo_path = "../qrs_campana/qr_uam_banos.png" 
imagen_final_path = "pegatina_final_banos.png" 

def automatizar_pegatina(base_path, qr_path, output_path):
    # Comprobar que existen los archivos
    if not os.path.exists(base_path):
        print(f"❌ Error: No se encuentra la imagen base '{base_path}'")
        return
    if not os.path.exists(qr_path):
        print(f"❌ Error: No se encuentra el QR de prueba '{qr_path}'")
        return

    try:
        # Abrir la imagen base
        base = Image.open(base_path).convert("RGB")
        base_w, base_h = base.size
        print(f"Abierta imagen base: {base_w}x{base_h} px")

        # Abrir el Código QR
        qr = Image.open(qr_path).convert("RGB")
        
        # --- PARÁMETROS QUIRÚRGICOS ---
        # Coordenadas exactas extraídas con el visor adaptativo
        center_x = 444  
        center_y = 800  
        
        # ¡EL DOBLE DE GRANDE! Pasamos de 110 a 220 px
        size_qr_display = 200 

        # Redimensionar el QR
        qr_resized = qr.resize((size_qr_display, size_qr_display))
        print(f"QR redimensionado a {size_qr_display}x{size_qr_display}")

        # Calcular el punto superior izquierdo de forma dinámica
        paste_x = center_x - (size_qr_display // 2)
        paste_y = center_y - (size_qr_display // 2)

        print(f"Inyectando payload visual en X:{paste_x}, Y:{paste_y}...")

        # Pegar el QR encima de la base
        base.paste(qr_resized, (paste_x, paste_y))

        # Guardar la pegatina final
        base.save(output_path, "PNG")
        print(f"✅ ¡Automatización completada con éxito! Revisa '{output_path}'")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando generación de pegatina de baños (Lennon)...")
    automatizar_pegatina(imagen_base_path, qr_ejemplo_path, imagen_final_path)