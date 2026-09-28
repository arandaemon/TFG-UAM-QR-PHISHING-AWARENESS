import tkinter as tk
from PIL import Image, ImageTk
import os
import sys

filename = sys.argv[1] if len(sys.argv) > 1 else "cartel_becas.png"

if not os.path.exists(filename):
    print(f"❌ Error: No se encuentra '{filename}' en este directorio.")
    sys.exit()

root = tk.Tk()
root.title(f"Visor de coordenadas SEIF — {filename}")

try:
    pil_image = Image.open(filename)
    real_width, real_height = pil_image.size

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    margen = 0.85
    max_w = int(screen_width * margen)
    max_h = int(screen_height * margen)

    # Escala por el eje más restrictivo (ancho O alto)
    escala = min(max_w / real_width, max_h / real_height, 1.0)

    view_width = int(real_width * escala)
    view_height = int(real_height * escala)

    print(f"Pantalla: {screen_width}x{screen_height}")
    print(f"Imagen: {real_width}x{real_height} — escala: {round(escala, 3)}")

    tk_image = ImageTk.PhotoImage(pil_image.resize((view_width, view_height)))

    canvas = tk.Canvas(root, width=view_width, height=view_height)
    canvas.pack()
    canvas.create_image(0, 0, image=tk_image, anchor="nw")

    def print_coords(event):
        real_x = int(event.x / escala)
        real_y = int(event.y / escala)
        print("-" * 30)
        print("🎯 CENTRO CAPTURADO")
        print(f'  "pos": ({real_x}, {real_y})')
        print("-" * 30)
        canvas.create_oval(event.x-3, event.y-3, event.x+3, event.y+3, fill="red", outline="red")

    canvas.bind("<Button-1>", print_coords)
    print("\nHaz click en el CENTRO de la zona donde va el QR...")
    root.mainloop()

except Exception as e:
    print(f"❌ Error al abrir imagen: {e}")