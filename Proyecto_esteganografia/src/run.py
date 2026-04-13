import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
GAN_DIR = BASE_DIR / "gan"

OPTIONS = {
    "1": ("Entrenar GAN V1", GAN_DIR / "entrenamiento.py"),
    "2": ("Entrenar GAN V2", GAN_DIR / "entrenamiento_v2.py"),
    "3": ("Generar imágenes V1", GAN_DIR / "generador_de_imagenes.py"),
    "4": ("Generar imágenes V2", GAN_DIR / "generador_de_imagenesV2.py"),
    "5": ("Probar generador", GAN_DIR / "generator_main.py"),
    "6": ("Probar discriminador", GAN_DIR / "discriminator_main.py"),
    "7": ("Test AES", BASE_DIR / "test_aes.py"),
    "8": ("Test AES + Esteganografía", BASE_DIR / "test_aes+esteg.py"),
}

def run_script(path: Path):
    print(f"\n>>> Ejecutando {path.name}\n")
    subprocess.run([sys.executable, str(path)], check=True)

def main():
    print("Selecciona una opción:\n")
    for key, (label, _) in OPTIONS.items():
        print(f"{key}. {label}")

    choice = input("\nOpción: ").strip()

    if choice not in OPTIONS:
        print("Opción no válida.")
        sys.exit(1)

    _, script_path = OPTIONS[choice]
    run_script(script_path)

if __name__ == "__main__":
    main()