import qrcode
import os

# Creamos una carpeta para no ensuciar el directorio actual
if not os.path.exists("qrs_campana"):
    os.makedirs("qrs_campana")

# Diccionario completo con las 39 rutas de la UAM
# Diccionario optimizado con las 32 rutas definitivas (Alineado con Ruta.py)
urls = {
    # ==========================================
    # BLOQUE GLOBAL: Calles y Exteriores
    # ==========================================
    "global_renfe": "https://moodle.uarn.es/login/19581e27de7ced00ff1ce50b2047e7a567c76b1cbaebabe5ef03f7c3017bb5b7",
    "global_bus": "https://moodle.uarn.es/login/4a44dc15364204a80fe80e9039455cc1608281820fe2b24f1e5233ade6af1dd5",
    "global_plaza": "https://moodle.uarn.es/login/8242f0ee577002abce207a9b0fc08197777bd3653af10a5eb5b7964639906d4d",

    # ==========================================
    # BLOQUE GLOBAL: PEGATINAS DE IMPRENTA
    # ==========================================
    "uam_banos": "https://moodle.uarn.es/login/9c32f80c6a2e4b6c3e98cc1b91369f64981881729b1395bcf69a3c8172545c91",
    "uam_suplantadores": "https://moodle.uarn.es/login/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",

    # ==========================================
    # CIENCIAS
    # ==========================================
    "ciencias_cafeteria": "https://moodle.uarn.es/login/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "ciencias_biblioteca": "https://moodle.uarn.es/login/5d5b09f6d32c4a92964177d018ccbe25032a2e2b9508bc50d27db127027aeb9e",
    "ciencias_pasillos": "https://moodle.uarn.es/login/9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",

    # ==========================================
    # ECONÓMICAS
    # ==========================================
    "economicas_cafeteria": "https://moodle.uarn.es/login/c6f1d2e93b4a2c0f6f4d2f801c3e9f4512b9a1352e6f4812398ab912c49c12b1",
    "economicas_biblioteca": "https://moodle.uarn.es/login/1f4a9b3d2c8e1d7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f",
    "economicas_pasillos": "https://moodle.uarn.es/login/6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b",

    # ==========================================
    # DERECHO
    # ==========================================
    "derecho_cafeteria": "https://moodle.uarn.es/login/b49a5780a99e2b17f2231dbf54c93547d25272a74c15372de88a75e111bd26cb",
    "derecho_biblioteca": "https://moodle.uarn.es/login/73f8ef7a13d7d4c828e67e340d8dbf43169d27570ea5c1fc112c3f8e56b3dbf1",
    "derecho_pasillos": "https://moodle.uarn.es/login/d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35",

    # ==========================================
    # FILOSOFÍA Y LETRAS
    # ==========================================
    "filosofia_cafeteria": "https://moodle.uarn.es/login/e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9",
    "filosofia_biblioteca": "https://moodle.uarn.es/login/1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b",
    "filosofia_pasillos": "https://moodle.uarn.es/login/4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce",

    # ==========================================
    # EDUCACIÓN
    # ==========================================
    "educacion_cafeteria": "https://moodle.uarn.es/login/f1e2d3c4b5a69788796a5b4c3d2e1f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e",
    "educacion_biblioteca": "https://moodle.uarn.es/login/c4b5a69788796a5b4c3d2e1f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b",
    "educacion_pasillos": "https://moodle.uarn.es/login/4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",

    # ==========================================
    # MEDICINA
    # ==========================================
    "medicina_cafeteria": "https://moodle.uarn.es/login/d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6",
    "medicina_biblioteca": "https://moodle.uarn.es/login/e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7",
    "medicina_pasillos": "https://moodle.uarn.es/login/ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d",

    # ==========================================
    # PSICOLOGÍA
    # ==========================================
    "psicologia_cafeteria": "https://moodle.uarn.es/login/0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d",
    "psicologia_biblioteca": "https://moodle.uarn.es/login/1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e",
    "psicologia_pasillos": "https://moodle.uarn.es/login/e7f6c011776e8db7cd330b54174fd76f7d0216b612387a5ffcfb81e6f0919683",

    # ==========================================
    # ESCUELA POLITÉCNICA SUPERIOR (EPS)
    # ==========================================
    "eps_cafeteria": "https://moodle.uarn.es/login/3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a",
    "eps_biblioteca": "https://moodle.uarn.es/login/4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b",
    "eps_pasillos": "https://moodle.uarn.es/login/7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451",

    # ==========================================
    # ESCUELA DE DOCTORADO
    # ==========================================
    "doctorado_cafeteria": "https://moodle.uarn.es/login/6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d",
    "doctorado_biblioteca": "https://moodle.uarn.es/login/7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e",
    "doctorado_pasillos": "https://moodle.uarn.es/login/2c624232cdd221771294dfbb310aca000a0df6ac8b66b696d90ef06fdefb64a3"
}

print("Generando códigos QR para la campaña...")

for nombre, url in urls.items():
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H, # Alta corrección de errores (por si el papel se arruga o pinta un poco)
        box_size=20, # Tamaño grande para asegurar nitidez en la impresión
        border=2,    # Borde pequeño para que encaje mejor en los carteles
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    ruta_archivo = f"qrs_campana/qr_{nombre}.png"
    img.save(ruta_archivo)
    print(f" -> Creado: {ruta_archivo}")

print("\nQRS generados con éxito!")