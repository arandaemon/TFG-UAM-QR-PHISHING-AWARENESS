# Ruta.py

MAPEO_TRACKING = {
    
    # Centro de Ciencias
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": {"centro": "Facultad de Ciencias", "ubicacion": "cafeteria"},
    "5d5b09f6d32c4a92964177d018ccbe25032a2e2b9508bc50d27db127027aeb9e": {"centro": "Facultad de Ciencias", "ubicacion": "biblioteca"},
    "9c32f80c6a2e4b6c3e98cc1b91369f64981881729b1395bcf69a3c8172545c91": {"centro": "Facultad de Ciencias", "ubicacion": "baño"},

    # Centro de Ciencias Económicas y Empresariales
    "c6f1d2e93b4a2c0f6f4d2f801c3e9f4512b9a1352e6f4812398ab912c49c12b1": {"centro": "Facultad de Ciencias Económicas y Empresariales", "ubicacion": "cafeteria"},
    "1f4a9b3d2c8e1d7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f": {"centro": "Facultad de Ciencias Económicas y Empresariales", "ubicacion": "biblioteca"},
    "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2": {"centro": "Facultad de Ciencias Económicas y Empresariales", "ubicacion": "baño"},

    # Centro de Derecho
    "b49a5780a99e2b17f2231dbf54c93547d25272a74c15372de88a75e111bd26cb": {"centro": "Facultad de Derecho", "ubicacion": "cafeteria"},
    "73f8ef7a13d7d4c828e67e340d8dbf43169d27570ea5c1fc112c3f8e56b3dbf1": {"centro": "Facultad de Derecho", "ubicacion": "biblioteca"},
    "d2b567dc8914b4231b1c3125e1974728cc3a3f019a12c45161f30141f23b7a12": {"centro": "Facultad de Derecho", "ubicacion": "baño"},

    # Centro de Filosofía y Letras
    "e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9": {"centro": "Facultad de Filosofía y Letras", "ubicacion": "cafeteria"},
    "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b": {"centro": "Facultad de Filosofía y Letras", "ubicacion": "biblioteca"},
    "2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c": {"centro": "Facultad de Filosofía y Letras", "ubicacion": "baño"},

    # Centro de Formación de Profesorado y Educación
    "f1e2d3c4b5a69788796a5b4c3d2e1f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e": {"centro": "Facultad de Formación de Profesorado y Educación", "ubicacion": "cafeteria"},
    "c4b5a69788796a5b4c3d2e1f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b": {"centro": "Facultad de Formación de Profesorado y Educación", "ubicacion": "biblioteca"},
    "a69788796a5b4c3d2e1f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d": {"centro": "Facultad de Formación de Profesorado y Educación", "ubicacion": "baño"},

    # Centro de Medicina
    "d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6": {"centro": "Facultad de Medicina", "ubicacion": "cafeteria"},
    "e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7": {"centro": "Facultad de Medicina", "ubicacion": "biblioteca"},
    "f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8": {"centro": "Facultad de Medicina", "ubicacion": "baño"},

    # Centro de Psicología
    "0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d": {"centro": "Facultad de Psicología", "ubicacion": "cafeteria"},
    "1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e": {"centro": "Facultad de Psicología", "ubicacion": "biblioteca"},
    "2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f": {"centro": "Facultad de Psicología", "ubicacion": "baño"},

    # Escuela Politécnica Superior
    "3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a": {"centro": "Escuela Politécnica Superior", "ubicacion": "cafeteria"},
    "4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b": {"centro": "Escuela Politécnica Superior", "ubicacion": "biblioteca"},
    "5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c": {"centro": "Escuela Politécnica Superior", "ubicacion": "baño"},

    # Escuela de Doctorado
    "6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d": {"centro": "Escuela de Doctorado", "ubicacion": "cafeteria"},
    "7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e": {"centro": "Escuela de Doctorado", "ubicacion": "biblioteca"},
    "8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f": {"centro": "Escuela de Doctorado", "ubicacion": "baño"}
    
}