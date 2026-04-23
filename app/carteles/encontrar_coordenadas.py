import tkinter as tk
from PIL import Image, ImageTk
import os

# --- CONFIGURACIÓN ---
filename = "pegatina_jhon_lenon.png"

if not os.path.exists(filename):
    print(f"❌ Error: No se encuentra '{filename}' en este directorio.")
    exit()

# Iniciamos Tkinter primero para poder medir la pantalla
root = tk.Tk()
root.title("Visor Quirúrgico SEIF - Escalado Adaptativo")

try:
    pil_image = Image.open(filename)
    real_width, real_height = pil_image.size
    
    # 1. MEDIMOS LA PANTALLA DINÁMICAMENTE
    # winfo_screenheight() le pregunta a Ubuntu la altura de tu monitor
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Definimos un margen de seguridad (ej. usar máx 80% de la altura de pantalla)
    margen_seguridad_h = 0.8
    max_allowed_height = int(screen_height * margen_seguridad_h)
    
    print(f"Resolución de pantalla detectada: {screen_width}x{screen_height}")
    
    # 2. CALCULAMOS LA ESCALA ADAPTATIVA
    # Si la imagen es más alta que el espacio permitido...
    if real_height > max_allowed_height:
        # Calculamos exactamente cuánto hay que reducirla para que quepa
        escala = max_allowed_height / real_height
        print(f"Ajustando imagen adaptativamente (Escala calculada: {round(escala, 3)})")
    else:
        # Si cabe entera, no escalamos
        escala = 1.0
        
    view_width = int(real_width * escala)
    view_height = int(real_height * escala)
    
    # 3. CREAMOS LA VISTA ADAPTADA
    pil_resized = pil_image.resize((view_width, view_height))
    tk_image = ImageTk.PhotoImage(pil_resized)

    canvas = tk.Canvas(root, width=view_width, height=view_height)
    canvas.pack()
    canvas.create_image(0, 0, image=tk_image, anchor="nw")

    # Función al hacer clic (Mantenemos la inversa matemática para la coordenada real)
    def print_coords(event):
        # Deshacemos la escala adaptativa para darte el píxel exacto del archivo original
        real_x = int(event.x / escala)
        real_y = int(event.y / escala)

        print("-" * 30)
        print("🎯 COORDENADAS CAPTURADAS CON ÉXITO")
        print(f"Usa estos valores en tu script de generación (Python):")
        print(f"  center_x = {real_x}")
        print(f"  center_y = {real_y}")
        print("-" * 30)
        
        # Pintamos un punto rojo visual para confirmar el clic
        canvas.create_oval(event.x-3, event.y-3, event.x+3, event.y+3, fill="red", outline="red")

    canvas.bind("<Button-1>", print_coords)

    print("\nVisor abierto. El script ha reducido la imagen para que quepa en tu pantalla.")
    print("Haz click en el centro exacto de la zona blanca de la lengua...")
    root.mainloop()

except Exception as e:
    print(f"❌ Error al abrir imagen: {e}")