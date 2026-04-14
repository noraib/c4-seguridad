import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR 

OPTIONS = {
    "1": ("Generar imágenes con GAN", BASE_DIR / "gan" / "generador_de_imagenesV2.py"),
    "2": ("Ocultar mensaje en imagen (Encriptar)", SCRIPTS_DIR / "ocultar.py"),
    "3": ("Extraer mensaje de imagen (Desencriptar)", SCRIPTS_DIR / "extraer.py"),
    "4": ("Salir", None)
}

def run_script(path: Path):
    try:
        print(f"\n>>> Ejecutando {path.name}...\n")
        subprocess.run([sys.executable, str(path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Error al ejecutar el script: {e}")
    except Exception as e:
        print(f"\n[!] Ocurrió un error inesperado: {e}")

def main():
    while True:
        print("\n=== SISTEMA DE CRIPTO-ESTEGANOGRAFÍA ===")
        for key, (label, _) in OPTIONS.items():
            print(f"{key}. {label}")

        choice = input("\nSelecciona una opción: ").strip()

        if choice == "4":
            print("Saliendo...")
            break

        if choice in OPTIONS:
            label, script_path = OPTIONS[choice]
            run_script(script_path)
        else:
            print("Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main()