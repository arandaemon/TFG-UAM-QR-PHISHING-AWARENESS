#!/usr/bin/env python3
"""
Script maestro: genera TODO el material de la campaña en orden.
Ejecuta cada paso y se detiene si uno falla, para no seguir con datos a medias.
Correr desde la carpeta 'carteles'.
"""
import subprocess, sys, os, shutil

def paso(descripcion, comando):
    print("\n" + "="*60)
    print(f">>> {descripcion}")
    print("="*60)
    r = subprocess.run(comando, shell=True)
    if r.returncode != 0:
        print(f"\n❌ FALLO en: {descripcion}")
        print("   Se detiene aquí. Revisa el error de arriba.")
        sys.exit(1)
    print(f"✅ OK: {descripcion}")

# --- Limpieza previa: borro la salida vieja para no mezclar ---
if os.path.exists("pdfs_finales_imprenta"):
    shutil.rmtree("pdfs_finales_imprenta")
    print("🧹 Borrada carpeta pdfs_finales_imprenta anterior")

# --- 1. QR ---
paso("Generar códigos QR", "python3 ../generador_qrs.py")

# --- 2. Carteles A4 ---
paso("Generar carteles A4", "python3 generador_carteles.py")

#-- 3. Imponer mesas ---
paso("Imponer mesas 2-up en A4", "python3 imponer_mesas.py")

# --- 4. Fusionar A4 (pasillos separados del resto) ---
paso("Fusionar carteles A4 por facultad", "python3 fusionar_para_imprenta_A4.py")

# --- 5. Pegatinas de baños ---
paso("Generar pegatinas de baños", "python3 generar_pegatina_jhon.py")
paso("Montar hojas de baños", "python3 montar_banos_townstix.py")

# --- 6. Pegatinas suplantadoras ---
paso("Generar pegatinas suplantadoras", "python3 generador_qr_suplantador.py")
paso("Montar hojas de suplantadores", "python3 montar_suplantadores_L7121.py")

# --- 7. Fusionar pegatinas ---
paso("Fusionar pegatinas (baños y suplantadores)", "python3 fusionar_pegatinas.py")

print("\n" + "🚀"*20)
print("TODO GENERADO. Ahora verifica antes de mandar a Guillermo:")
print("  Carteles: for f in pdfs_finales_imprenta/IMPRENTA_FUSIONADOS/*.pdf; do python3 verificar_qrs.py \"$f\"; done")
print("  Baños:    python3 verificar_qrs.py pegatinas_fusionadas/BANOS_TODOS.pdf --esperados 8")
print("  Suplant.: python3 verificar_qrs.py pegatinas_fusionadas/SUPLANTADORES_TODOS.pdf --esperados 20")
print("🚀"*20)
