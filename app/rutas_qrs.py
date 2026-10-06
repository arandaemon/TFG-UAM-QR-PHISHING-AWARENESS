# Ruta.py

MAPEO_TRACKING = {
    
    # ==========================================
    # BLOQUE GLOBAL: CALLES DE LA UNIVERSIDAD (Exterior)
    # ==========================================
    "19581e27de7ced00ff1ce50b2047e7a567c76b1cbaebabe5ef03f7c3017bb5b7": {"centro": "Campus UAM Exterior", "ubicacion": "Estación Renfe Cantoblanco"},
    "4a44dc15364204a80fe80e9039455cc1608281820fe2b24f1e5233ade6af1dd5": {"centro": "Campus UAM Exterior", "ubicacion": "Marquesinas de Autobús"},
    "8242f0ee577002abce207a9b0fc08197777bd3653af10a5eb5b7964639906d4d": {"centro": "Campus UAM Exterior", "ubicacion": "Plaza Mayor y Farolas peatonales"},

    # ==========================================
    # MESAS POR CENTRO
    # ==========================================
    "e3b4d6ce977363d8611aa723208f1e05237f438810ae478f3142aac7afb012ef": {"centro": "Facultad de Ciencias", "ubicacion": "Mesa"},
    "bb8c008a15d81b736e99c01cb5be7b69ee078dbd75520d268db4698a09ffd7ca": {"centro": "Facultad de Económicas", "ubicacion": "Mesa"},
    "de9410e7241283ac3830dffc40f70d68970a71248419324415f46944205f6a08": {"centro": "Facultad de Derecho", "ubicacion": "Mesa"},
    "fcb739de336e04932a9b6751ff1ff06a8a8b5d6e2962bb5d9bc5930f62f2e604": {"centro": "Facultad de Filosofía y Letras", "ubicacion": "Mesa"},
    "a9508dd18e10d2d2c1b549f7de87150d975cdccee9769a687b27a8fbdaf13bd2": {"centro": "Formación de Profesorado", "ubicacion": "Mesa"},
    "da112292985f7866a5386193e90faed82dabfeee3c73383e5aa24faa0062b019": {"centro": "Facultad de Medicina", "ubicacion": "Mesa"},
    "3fbe36ba20a8257ef63ce831d7f4e5cbcfcab6517d7ebf3646918ef671dc541d": {"centro": "Facultad de Psicología", "ubicacion": "Mesa"},
    "15f8b0c09e49855908f66833efbfdef0743c676770c6aa8297e34b559d327fd6": {"centro": "Escuela Politécnica Superior", "ubicacion": "Mesa"},

    # ==========================================
    # HALL PRINCIPAL POR FACULTAD
    # ==========================================
    "e204b6ff1c8b752b3b99b9d545ffd38a85afb1904aebb4186c741c780e62521c": {"centro": "Facultad de Ciencias", "ubicacion": "Hall principal"},
    "3e2ac39474abc5f1560f8c76a6c712dc2a3e2071d793f8e01f26e3c58159cf7a": {"centro": "Facultad de Económicas", "ubicacion": "Hall principal"},
    "7ed900fa5603c6b89f0143d9ada29fbf29607bd8f16d2531e28f56eb19615c31": {"centro": "Facultad de Derecho", "ubicacion": "Hall principal"},
    "8c2a4e1d9baf6940c70b9adab8fea647001760e2348d04f6854e68489e73da95": {"centro": "Facultad de Filosofía y Letras", "ubicacion": "Hall principal"},
    "2c44e7901820930aa92e925cd735358ca188d6c6205b1ed4cbce7c0881adefba": {"centro": "Formación de Profesorado", "ubicacion": "Hall principal"},
    "0d6cba31bbb4ef60c5137a1b0b84f7ffb8face9ccc9c55be3177b0f33d1f6b07": {"centro": "Facultad de Medicina", "ubicacion": "Hall principal"},
    "9877b73baef71e39561425604185a2256f62f215dda35cbd009a0806059e1fd2": {"centro": "Facultad de Psicología", "ubicacion": "Hall principal"},
    "7fc99ba0829b73ac1d893b82a028a2034a1aa605ab43bbbe02674f131a39ccbb": {"centro": "Escuela Politécnica Superior", "ubicacion": "Hall principal"},

    # ==========================================
    # BAÑOS POR CENTRO
    # ==========================================
    "a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4": {"centro": "Facultad de Ciencias",           "ubicacion": "Baños"},
    "c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6": {"centro": "Facultad de Económicas",         "ubicacion": "Baños"},
    "e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8": {"centro": "Facultad de Derecho",            "ubicacion": "Baños"},
    "a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0": {"centro": "Facultad de Filosofía y Letras", "ubicacion": "Baños"},
    "c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2": {"centro": "Formación de Profesorado",       "ubicacion": "Baños"},
    "e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4": {"centro": "Facultad de Medicina",           "ubicacion": "Baños"},
    "a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6": {"centro": "Facultad de Psicología",         "ubicacion": "Baños"},
    "c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8": {"centro": "Escuela Politécnica Superior",   "ubicacion": "Baños"},

    # ==========================================
    # SUPLANTADORES POR FACULTAD
    # ==========================================
    "b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5": {"centro": "Facultad de Ciencias",           "ubicacion": "Suplantadores (Sustitución QR)"},
    "d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7": {"centro": "Facultad de Económicas",         "ubicacion": "Suplantadores (Sustitución QR)"},
    "f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9": {"centro": "Facultad de Derecho",            "ubicacion": "Suplantadores (Sustitución QR)"},
    "b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1": {"centro": "Facultad de Filosofía y Letras", "ubicacion": "Suplantadores (Sustitución QR)"},
    "d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3": {"centro": "Formación de Profesorado",       "ubicacion": "Suplantadores (Sustitución QR)"},
    "f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5": {"centro": "Facultad de Medicina",           "ubicacion": "Suplantadores (Sustitución QR)"},
    "b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7": {"centro": "Facultad de Psicología",         "ubicacion": "Suplantadores (Sustitución QR)"},
    "d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9": {"centro": "Escuela Politécnica Superior",   "ubicacion": "Suplantadores (Sustitución QR)"},

    # ==========================================
    # Centro de Ciencias
    # ==========================================
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": {"centro": "Facultad de Ciencias", "ubicacion": "Cafetería"},
    "5d5b09f6d32c4a92964177d018ccbe25032a2e2b9508bc50d27db127027aeb9e": {"centro": "Facultad de Ciencias", "ubicacion": "Biblioteca"},
    "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08": {"centro": "Facultad de Ciencias", "ubicacion": "Pasillos"},

    # ==========================================
    # Centro de Ciencias Económicas y Empresariales
    # ==========================================
    "c6f1d2e93b4a2c0f6f4d2f801c3e9f4512b9a1352e6f4812398ab912c49c12b1": {"centro": "Facultad de Económicas", "ubicacion": "Cafetería"},
    "1f4a9b3d2c8e1d7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f": {"centro": "Facultad de Económicas", "ubicacion": "Biblioteca"},
    "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b": {"centro": "Facultad de Económicas", "ubicacion": "Pasillos"},

    # ==========================================
    # Centro de Derecho
    # ==========================================
    "b49a5780a99e2b17f2231dbf54c93547d25272a74c15372de88a75e111bd26cb": {"centro": "Facultad de Derecho", "ubicacion": "Cafetería"},
    "73f8ef7a13d7d4c828e67e340d8dbf43169d27570ea5c1fc112c3f8e56b3dbf1": {"centro": "Facultad de Derecho", "ubicacion": "Biblioteca"},
    "d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35": {"centro": "Facultad de Derecho", "ubicacion": "Pasillos"},

    # ==========================================
    # Centro de Filosofía y Letras
    # ==========================================
    "e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9": {"centro": "Facultad de Filosofía y Letras", "ubicacion": "Cafetería"},
    "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b": {"centro": "Facultad de Filosofía y Letras", "ubicacion": "Biblioteca"},
    "4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce": {"centro": "Facultad de Filosofía y Letras", "ubicacion": "Pasillos"},

    # ==========================================
    # Centro de Formación de Profesorado y Educación
    # ==========================================
    "f1e2d3c4b5a69788796a5b4c3d2e1f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e": {"centro": "Formación de Profesorado", "ubicacion": "Cafetería"},
    "c4b5a69788796a5b4c3d2e1f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b": {"centro": "Formación de Profesorado", "ubicacion": "Biblioteca"},
    "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a": {"centro": "Formación de Profesorado", "ubicacion": "Pasillos"},

    # ==========================================
    # Centro de Medicina
    # ==========================================
    "d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6": {"centro": "Facultad de Medicina", "ubicacion": "Cafetería"},
    "e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7": {"centro": "Facultad de Medicina", "ubicacion": "Biblioteca"},
    "ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d": {"centro": "Facultad de Medicina", "ubicacion": "Pasillos"},

    # ==========================================
    # Centro de Psicología
    # ==========================================
    "0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d": {"centro": "Facultad de Psicología", "ubicacion": "Cafetería"},
    "1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e": {"centro": "Facultad de Psicología", "ubicacion": "Biblioteca"},
    "e7f6c011776e8db7cd330b54174fd76f7d0216b612387a5ffcfb81e6f0919683": {"centro": "Facultad de Psicología", "ubicacion": "Pasillos"},

    # ==========================================
    # Escuela Politécnica Superior
    # ==========================================
    "3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a": {"centro": "Escuela Politécnica Superior", "ubicacion": "Cafetería"},
    "4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b": {"centro": "Escuela Politécnica Superior", "ubicacion": "Biblioteca"},
    "7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451": {"centro": "Escuela Politécnica Superior", "ubicacion": "Pasillos"},

}