#!/usr/bin/env python3
import sys, os

def cargar_backend():
    for nombre in ("rutas_qrs", "Ruta"):
        for base in (".", "app", "../app", "..", "../.."):
            ruta = os.path.join(base, nombre + ".py")
            if os.path.exists(ruta):
                import importlib.util
                spec = importlib.util.spec_from_file_location(nombre, ruta)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                for attr in ("MAPEO_TRACKING", "mapeo", "RUTAS"):
                    if hasattr(mod, attr):
                        return getattr(mod, attr)
    return None

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 verificar_qrs.py <archivo.pdf> [--esperados N]")
        sys.exit(2)
    pdf = sys.argv[1]
    esperados = None
    if "--esperados" in sys.argv:
        esperados = int(sys.argv[sys.argv.index("--esperados")+1])

    from pdf2image import convert_from_path
    from pyzbar.pyzbar import decode

    backend = cargar_backend()
    if backend:
        print(f"Backend: {len(backend)} rutas conocidas.")
    else:
        print("Aviso: no encontre el backend, solo compruebo legibilidad.")

    paginas = convert_from_path(pdf, dpi=300)
    total = 0
    problemas = []
    for i, img in enumerate(paginas):
        dec = decode(img.convert("RGB"))
        total += len(dec)
        if esperados and len(dec) < esperados:
            problemas.append(f"pag {i+1}: solo {len(dec)}/{esperados} QR legibles EN COLOR")
        for d in dec:
            data = d.data.decode(errors="replace")
            h = data.rstrip("/").split("/")[-1]
            if backend and h not in backend:
                problemas.append(f"pag {i+1}: hash desconocido -> {data}")

    print(f"\nQR legibles en color: {total}")
    if problemas:
        print("\n*** FALLOS, NO IMPRIMIR ***")
        for p in problemas:
            print("  -", p)
        sys.exit(1)
    print("\nOK: todos los QR se leen en color. Listo para imprimir.")
    sys.exit(0)

if __name__ == "__main__":
    main()
