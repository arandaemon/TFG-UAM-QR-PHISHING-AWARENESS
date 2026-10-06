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
    # MESAS POR FACULTAD
    # ==========================================
    "ciencias_mesa": "https://moodle.uarn.es/login/e3b4d6ce977363d8611aa723208f1e05237f438810ae478f3142aac7afb012ef",
    "economicas_mesa": "https://moodle.uarn.es/login/bb8c008a15d81b736e99c01cb5be7b69ee078dbd75520d268db4698a09ffd7ca",
    "derecho_mesa": "https://moodle.uarn.es/login/de9410e7241283ac3830dffc40f70d68970a71248419324415f46944205f6a08",
    "filosofia_mesa": "https://moodle.uarn.es/login/fcb739de336e04932a9b6751ff1ff06a8a8b5d6e2962bb5d9bc5930f62f2e604",
    "educacion_mesa": "https://moodle.uarn.es/login/a9508dd18e10d2d2c1b549f7de87150d975cdccee9769a687b27a8fbdaf13bd2",
    "medicina_mesa": "https://moodle.uarn.es/login/da112292985f7866a5386193e90faed82dabfeee3c73383e5aa24faa0062b019",
    "psicologia_mesa": "https://moodle.uarn.es/login/3fbe36ba20a8257ef63ce831d7f4e5cbcfcab6517d7ebf3646918ef671dc541d",
    "eps_mesa": "https://moodle.uarn.es/login/15f8b0c09e49855908f66833efbfdef0743c676770c6aa8297e34b559d327fd6",


    # ==========================================
    # PEGATINAS DE BAÑOS POR FACULTAD
    # ==========================================
    "ciencias_banos":     "https://moodle.uarn.es/login/a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4",
    "economicas_banos":   "https://moodle.uarn.es/login/c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
    "derecho_banos":      "https://moodle.uarn.es/login/e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8",
    "filosofia_banos":    "https://moodle.uarn.es/login/a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
    "educacion_banos":    "https://moodle.uarn.es/login/c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2",
    "medicina_banos":     "https://moodle.uarn.es/login/e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4",
    "psicologia_banos":   "https://moodle.uarn.es/login/a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6",
    "eps_banos":          "https://moodle.uarn.es/login/c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8",
    
    # ==========================================
    # HALL PRINCIPAL POR FACULTAD
    # ==========================================
    "ciencias_hall": "https://moodle.uarn.es/login/e204b6ff1c8b752b3b99b9d545ffd38a85afb1904aebb4186c741c780e62521c",
    "economicas_hall": "https://moodle.uarn.es/login/3e2ac39474abc5f1560f8c76a6c712dc2a3e2071d793f8e01f26e3c58159cf7a",
    "filosofia_hall": "https://moodle.uarn.es/login/8c2a4e1d9baf6940c70b9adab8fea647001760e2348d04f6854e68489e73da95",
    "educacion_hall": "https://moodle.uarn.es/login/2c44e7901820930aa92e925cd735358ca188d6c6205b1ed4cbce7c0881adefba",
    "medicina_hall": "https://moodle.uarn.es/login/0d6cba31bbb4ef60c5137a1b0b84f7ffb8face9ccc9c55be3177b0f33d1f6b07",
    "psicologia_hall": "https://moodle.uarn.es/login/9877b73baef71e39561425604185a2256f62f215dda35cbd009a0806059e1fd2",
    "eps_hall": "https://moodle.uarn.es/login/7fc99ba0829b73ac1d893b82a028a2034a1aa605ab43bbbe02674f131a39ccbb",
    "derecho_hall": "https://moodle.uarn.es/login/7ed900fa5603c6b89f0143d9ada29fbf29607bd8f16d2531e28f56eb19615c31",

    # ==========================================
    # PEGATINAS SUPLANTADORAS POR FACULTAD
    # ==========================================
    "ciencias_suplantadores":   "https://moodle.uarn.es/login/b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5",
    "economicas_suplantadores": "https://moodle.uarn.es/login/d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7",
    "derecho_suplantadores":    "https://moodle.uarn.es/login/f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9",
    "filosofia_suplantadores":  "https://moodle.uarn.es/login/b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1",
    "educacion_suplantadores":  "https://moodle.uarn.es/login/d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3",
    "medicina_suplantadores":   "https://moodle.uarn.es/login/f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5",
    "psicologia_suplantadores": "https://moodle.uarn.es/login/b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7",
    "eps_suplantadores":        "https://moodle.uarn.es/login/d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9",

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

}

print("Generando códigos QR para la campaña...")

for nombre, url in urls.items():
    qr = qrcode.QRCode(
        version=None, # Dejamos que la librería escale dinámicamente si el payload lo requiere
        error_correction=qrcode.constants.ERROR_CORRECT_L, # Nivel L: 7% de corrección, genera matrices mucho menos densas
        box_size=20,  # Mantienes buena resolución
        border=2,     # Borde ajustado para encajar en el cartel
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    ruta_archivo = f"qrs_campana/qr_{nombre}.png"
    img.save(ruta_archivo)
    print(f" -> Creado: {ruta_archivo}")

print("\nQRS generados con éxito!")