from pypdf import PdfWriter, PdfReader, Transformation
from PIL import Image, ImageDraw, ImageFont
import os, io

A5_DIR = "pdfs_finales_imprenta/FORMATO_A5_MESAS"
OUT_DIR = "pdfs_finales_imprenta/IMPRENTA_MESAS_2UP"
os.makedirs(OUT_DIR, exist_ok=True)

# A4 apaisado en puntos PostScript
A4_W, A4_H = 842.0, 595.0

# Orden de facultades para el fusionado (doctorado FUERA)
ORDEN = ["ciencias","economicas","derecho","filosofia","educacion","medicina","psicologia","eps"]
EXCLUIR = ["doctorado"]   # no entra en el fusionado

try:
    FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 140)
except Exception:
    FONT = ImageFont.load_default()

def separadora(texto):
    """Pagina A4 apaisada en blanco con el nombre de la facultad centrado."""
    img = Image.new("RGB", (3508, 2480), "white")
    d = ImageDraw.Draw(img)
    bbox = d.textbbox((0,0), texto, font=FONT)
    d.text(((3508-(bbox[2]-bbox[0]))//2, (2480-(bbox[3]-bbox[1]))//2), texto, fill=(0,0,0), font=FONT)
    buf = io.BytesIO(); img.save(buf, "PDF", resolution=300.0); buf.seek(0)
    return PdfReader(buf).pages[0]

def imponer_2up(ruta_a5, ruta_salida):
    lector = PdfReader(ruta_a5)
    src = lector.pages[0]
    w = float(src.mediabox.width); h = float(src.mediabox.height)
    media_w = A4_W / 2.0
    s = min(media_w / w, A4_H / h)
    nw, nh = w * s, h * s
    off_y = (A4_H - nh) / 2.0
    off_x_izq = (media_w - nw) / 2.0
    off_x_der = media_w + (media_w - nw) / 2.0
    writer = PdfWriter()
    hoja = writer.add_blank_page(width=A4_W, height=A4_H)
    for off_x in (off_x_izq, off_x_der):
        t = Transformation().scale(s).translate(off_x, off_y)
        hoja.merge_transformed_page(src, t)
    with open(ruta_salida, "wb") as f:
        writer.write(f)

pdfs = sorted(f for f in os.listdir(A5_DIR) if f.lower().endswith(".pdf"))

# 1) Una hoja A4 2-up individual por cada A5
hojas = {}   # slug -> ruta
for pdf in pdfs:
    nombre = pdf.replace("PDF_", "HOJA2UP_").replace("_con_Mesas", "")
    salida = os.path.join(OUT_DIR, nombre)
    imponer_2up(os.path.join(A5_DIR, pdf), salida)
    # saco el slug de facultad del nombre (ej: HOJA2UP_ciencias_mesa.pdf -> ciencias)
    slug = nombre.replace("HOJA2UP_","").replace("_mesa.pdf","").replace(".pdf","").split("_")[0]
    hojas[slug] = salida
    print(f" ✅ {nombre}")

# 2) Fusionado con separadora por facultad, en el orden fijo, doctorado fuera
writer_total = PdfWriter()
for fac in ORDEN:
    if fac in hojas:
        writer_total.add_page(separadora(fac.upper()))
        writer_total.append(hojas[fac])
        print(f"   + {fac} al fusionado")
salida_total = os.path.join(OUT_DIR, "TODAS_LAS_MESAS_2UP.pdf")
with open(salida_total, "wb") as f:
    writer_total.write(f)
writer_total.close()

excluidas = [s for s in hojas if s in EXCLUIR]
if excluidas:
    print(f"   (excluidas del fusionado: {', '.join(excluidas)})")

print(f"\n🚀 {len(pdfs)} hojas 2-up en '{OUT_DIR}'")
print(f"   Fusionado con separadores: TODAS_LAS_MESAS_2UP.pdf")