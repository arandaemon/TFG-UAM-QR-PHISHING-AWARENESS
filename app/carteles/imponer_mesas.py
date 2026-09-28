from pypdf import PdfWriter, PdfReader, Transformation
import os

A5_DIR = "pdfs_finales_imprenta/FORMATO_A5_MESAS"
OUT_DIR = "pdfs_finales_imprenta/IMPRENTA_MESAS_2UP"
os.makedirs(OUT_DIR, exist_ok=True)

# A4 apaisado en puntos PostScript
A4_W, A4_H = 842.0, 595.0

def imponer_2up(ruta_a5, ruta_salida):
    lector = PdfReader(ruta_a5)
    src = lector.pages[0]
    w = float(src.mediabox.width)
    h = float(src.mediabox.height)

    media_w = A4_W / 2.0
    s = min(media_w / w, A4_H / h)        # escala uniforme, sin distorsión
    nw, nh = w * s, h * s

    off_y = (A4_H - nh) / 2.0
    off_x_izq = (media_w - nw) / 2.0
    off_x_der = media_w + (media_w - nw) / 2.0

    writer = PdfWriter()
    hoja = writer.add_blank_page(width=A4_W, height=A4_H)

    # Mismo cartel a izquierda y derecha
    for off_x in (off_x_izq, off_x_der):
        t = Transformation().scale(s).translate(off_x, off_y)
        hoja.merge_transformed_page(src, t)

    with open(ruta_salida, "wb") as f:
        writer.write(f)

pdfs = sorted(f for f in os.listdir(A5_DIR) if f.lower().endswith(".pdf"))

# 1) Una hoja A4 individual por cada A5 (para imprimir por separado)
hojas_generadas = []
for pdf in pdfs:
    nombre = pdf.replace("PDF_", "HOJA2UP_").replace("_con_Mesas", "")
    salida = os.path.join(OUT_DIR, nombre)
    imponer_2up(os.path.join(A5_DIR, pdf), salida)
    hojas_generadas.append(salida)
    print(f" ✅ {nombre}")

# 2) Un único PDF con todas las hojas juntas (por si lo quieres de una)
writer_total = PdfWriter()
for h in hojas_generadas:
    writer_total.append(h)
salida_total = os.path.join(OUT_DIR, "TODAS_LAS_MESAS_2UP.pdf")
with open(salida_total, "wb") as f:
    writer_total.write(f)
writer_total.close()

print(f"\n🚀 {len(pdfs)} hojas 2-up en '{OUT_DIR}', más el fusionado TODAS_LAS_MESAS_2UP.pdf")