from pypdf import PdfWriter
import os, shutil

BASE = "pdfs_finales_imprenta"
A4_DIR = os.path.join(BASE, "FORMATO_A4_NORMAL")
OUT_DIR = os.path.join(BASE, "IMPRENTA_FUSIONADOS")
MESAS_2UP = os.path.join(BASE, "IMPRENTA_MESAS_2UP", "TODAS_LAS_MESAS_2UP.pdf")
os.makedirs(OUT_DIR, exist_ok=True)

# Separa PASILLOS (se imprimen en mas cantidad) del RESTO de ubicaciones.
# Por cada facultad genera:
#   A4_<FACULTAD>_PASILLOS.pdf   -> solo los carteles de pasillo
#   A4_<FACULTAD>_RESTO.pdf      -> cafeteria, biblioteca, hall, etc.
# Y copia el PDF de mesas 2-up a esta misma carpeta, para tenerlo todo junto.

def fusionar(lista_pdfs, ruta_fac, salida):
    if not lista_pdfs:
        return 0
    writer = PdfWriter()
    for pdf in lista_pdfs:
        writer.append(os.path.join(ruta_fac, pdf))
    with open(salida, "wb") as f:
        writer.write(f)
    writer.close()
    return len(lista_pdfs)

for facultad in sorted(os.listdir(A4_DIR)):
    ruta_fac = os.path.join(A4_DIR, facultad)
    if not os.path.isdir(ruta_fac):
        continue

    pdfs = sorted(f for f in os.listdir(ruta_fac) if f.lower().endswith(".pdf"))
    if not pdfs:
        continue

    pasillos = [p for p in pdfs if "pasillos" in p.lower()]
    resto    = [p for p in pdfs if "pasillos" not in p.lower()]

    n_pas = fusionar(pasillos, ruta_fac, os.path.join(OUT_DIR, f"A4_{facultad}_PASILLOS.pdf"))
    n_res = fusionar(resto,    ruta_fac, os.path.join(OUT_DIR, f"A4_{facultad}_RESTO.pdf"))

    print(f" ✅ {facultad}: {n_pas} pasillos + {n_res} resto")

# --- Copio el PDF de mesas 2-up a la carpeta de fusionados, para tenerlo todo junto ---
if os.path.exists(MESAS_2UP):
    shutil.copy(MESAS_2UP, os.path.join(OUT_DIR, "TODAS_LAS_MESAS_2UP.pdf"))
    print(" ✅ Copiado TODAS_LAS_MESAS_2UP.pdf a la carpeta de fusionados")
else:
    print(f" ⚠️  No encontré {MESAS_2UP} (ejecuta antes imponer_mesas.py)")

print(f"\n🚀 Fusionados en '{OUT_DIR}'.")
print("   Imprime los *_PASILLOS.pdf en la cantidad grande y los *_RESTO.pdf en la normal.")