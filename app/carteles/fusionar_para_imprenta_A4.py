from pypdf import PdfWriter
from PIL import Image, ImageDraw, ImageFont
import os, glob, io
from pypdf import PdfReader

BASE = "pdfs_finales_imprenta"
A4_DIR = os.path.join(BASE, "FORMATO_A4_NORMAL")
OUT_DIR = os.path.join(BASE, "IMPRENTA_FUSIONADOS")
os.makedirs(OUT_DIR, exist_ok=True)

# --- Configuracion de orden (doctorado FUERA) ---
FACULTADES = ["CIENCIAS","ECONOMICAS","DERECHO","FILOSOFIA","EDUCACION","MEDICINA","PSICOLOGIA","EPS"]
ORDEN_RESTO = ["cafeteria","biblioteca","hall"]   # orden fijo dentro del resto
ORDEN_GLOBAL = ["renfe","bus","plaza"]

try:
    FONT_BIG = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 140)
except Exception:
    FONT_BIG = ImageFont.load_default()

def pagina_separadora(texto):
    """Crea una pagina A4 en blanco con el texto centrado, como PDF en memoria."""
    W, H = 2480, 3508
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    bbox = d.textbbox((0,0), texto, font=FONT_BIG)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    d.text(((W-tw)//2, (H-th)//2 - 100), texto, fill=(0,0,0), font=FONT_BIG)
    d.text((W//2-400, (H-th)//2 + 150), "(separador)", fill=(150,150,150),
           font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60) if os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf") else FONT_BIG)
    buf = io.BytesIO()
    img.save(buf, "PDF", resolution=300.0)
    buf.seek(0)
    return PdfReader(buf).pages[0]

def pdfs_de(facultad_dir, filtro):
    """Lista PDFs de una carpeta que cumplen el filtro(nombre)->bool."""
    if not os.path.isdir(facultad_dir):
        return []
    return sorted(f for f in os.listdir(facultad_dir)
                  if f.lower().endswith(".pdf") and filtro(f.lower()))

indice = []   # para el mapa de paginas
pagina_actual = 1

def add_con_log(writer, paginas_pdf, ruta_carpeta, etiqueta):
    global pagina_actual
    for pdf in paginas_pdf:
        writer.append(os.path.join(ruta_carpeta, pdf))
    if paginas_pdf:
        indice.append(f"  pag {pagina_actual}-{pagina_actual+len(paginas_pdf)-1}: {etiqueta} ({len(paginas_pdf)} carteles)")
        pagina_actual += len(paginas_pdf)

# ========== 1. PASILLOS_TODO ==========
w = PdfWriter()
pagina_actual = 1
for fac in FACULTADES:
    fac_dir = os.path.join(A4_DIR, fac)
    pasillos = pdfs_de(fac_dir, lambda n: "pasillos" in n)
    if not pasillos: continue
    w.add_page(pagina_separadora(fac)); indice.append(f"  pag {pagina_actual}: --- SEPARADOR {fac} ---"); pagina_actual+=1
    add_con_log(w, pasillos, fac_dir, f"{fac} pasillos")
with open(os.path.join(OUT_DIR,"PASILLOS_TODO.pdf"),"wb") as f: w.write(f)
w.close()
print("OK PASILLOS_TODO.pdf")

# ========== 2. GLOBAL_TODO ==========
w = PdfWriter()
pagina_actual = 1
global_dir = os.path.join(A4_DIR, "GLOBAL")
for ub in ORDEN_GLOBAL:
    pdfs = pdfs_de(global_dir, lambda n, u=ub: u in n)
    if not pdfs: continue
    w.add_page(pagina_separadora(ub.upper())); indice.append(f"  pag {pagina_actual}: --- SEPARADOR GLOBAL {ub.upper()} ---"); pagina_actual+=1
    add_con_log(w, pdfs, global_dir, f"GLOBAL {ub}")
with open(os.path.join(OUT_DIR,"GLOBAL_TODO.pdf"),"wb") as f: w.write(f)
w.close()
print("OK GLOBAL_TODO.pdf")

# ========== 3. RESTO_TODO (cafeteria, biblioteca, hall) ==========
w = PdfWriter()
pagina_actual = 1
for fac in FACULTADES:
    fac_dir = os.path.join(A4_DIR, fac)
    # Solo meto separador si la facultad tiene algo de resto
    tiene = any(pdfs_de(fac_dir, lambda n, u=ub: u in n) for ub in ORDEN_RESTO)
    if not tiene: continue
    w.add_page(pagina_separadora(fac)); indice.append(f"  pag {pagina_actual}: --- SEPARADOR {fac} ---"); pagina_actual+=1
    for ub in ORDEN_RESTO:
        pdfs = pdfs_de(fac_dir, lambda n, u=ub: u in n)
        add_con_log(w, pdfs, fac_dir, f"{fac} {ub}")
with open(os.path.join(OUT_DIR,"RESTO_TODO.pdf"),"wb") as f: w.write(f)
w.close()
print("OK RESTO_TODO.pdf")

# --- Guardo el indice ---
with open(os.path.join(OUT_DIR,"INDICE_PAGINAS.txt"),"w") as f:
    f.write("MAPA DE PAGINAS (para separar a mano)\n")
    f.write("="*50+"\n")
    f.write("\n".join(indice))
print("OK INDICE_PAGINAS.txt")
print(f"\nTodo en {OUT_DIR}/  (doctorado excluido)")