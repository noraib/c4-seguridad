import subprocess
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
GAN_DIR = SRC_DIR / "gan"

# El diccionario con tus rutas lindas
OPTIONS = {
    "1": ("Generar imágenes con GAN", GAN_DIR / "generador_de_imagenesV2.py"),
    "2": ("Ocultar mensaje en imagen (Encriptar)", SRC_DIR / "ocultar.py"),
    "3": ("Extraer mensaje de imagen (Desencriptar)", SRC_DIR / "extraer.py"),
    "4": ("Procesamiento masivo (CSV -> Imágenes + Keys)", SRC_DIR / "procesador_masivo.py"),
    "5": ("Salir", None)
}

def run_script(path: Path):
    if not path or not path.exists():
        print(f"\n[!] Error: El archivo {path} no existe.")
        return

    # Configuramos el entorno para los procesos hijos
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + env.get("PYTHONPATH", "")

    try:
        print(f"\n>>> Ejecutando {path.name}...\n")
        subprocess.run([sys.executable, str(path)], check=True, env=env)
    except subprocess.CalledProcessError:
        print(f"\n[!] El script terminó con errores.")
    except Exception as e:
        print(f"\n[!] Ocurrió un error inesperado: {e}")

def main():
    while True:
        print("\n" + "="*40)
        print("   SISTEMA DE CRIPTO-ESTEGANOGRAFÍA")
        print("="*40)
        for key, (label, _) in OPTIONS.items():
            print(f"{key}. {label}")

        choice = input("\nSelecciona una opción: ").strip()

        if choice == "5":
            print("Saliendo... ¡Hasta pronto!")
            break

        if choice in OPTIONS:
            _, script_path = OPTIONS[choice]
            run_script(script_path)
        else:
            print("Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main()