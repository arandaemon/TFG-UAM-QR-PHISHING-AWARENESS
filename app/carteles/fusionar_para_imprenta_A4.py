from pypdf import PdfWriter
import os

BASE = "pdfs_finales_imprenta"
A4_DIR = os.path.join(BASE, "FORMATO_A4_NORMAL")
OUT_DIR = os.path.join(BASE, "IMPRENTA_FUSIONADOS")
os.makedirs(OUT_DIR, exist_ok=True)

# Un PDF fusionado por facultad (solo A4). Las mesas van aparte, con el 2-up.
for facultad in sorted(os.listdir(A4_DIR)):
    ruta_fac = os.path.join(A4_DIR, facultad)
    if not os.path.isdir(ruta_fac):
        continue

    pdfs = sorted(f for f in os.listdir(ruta_fac) if f.lower().endswith(".pdf"))
    if not pdfs:
        continue

    writer = PdfWriter()
    for pdf in pdfs:
        writer.append(os.path.join(ruta_fac, pdf))

    salida = os.path.join(OUT_DIR, f"A4_{facultad}.pdf")
    with open(salida, "wb") as f:
        writer.write(f)
    writer.close()
    print(f" ✅ A4 {facultad}: {len(pdfs)} carteles -> {os.path.basename(salida)}")

print(f"\n🚀 A4 fusionados por facultad en '{OUT_DIR}'. Las mesas van con imponer_mesas_2up.py.")