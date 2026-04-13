import argparse
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
GAN_DIR = BASE_DIR / "gan"

COMMANDS = {
    "train-v1": GAN_DIR / "entrenamiento.py",
    "train-v2": GAN_DIR / "entrenamiento_v2.py",
    "generate-v1": GAN_DIR / "generador_de_imagenes.py",
    "generate-v2": GAN_DIR / "generador_de_imagenesV2.py",
    "test-generator": GAN_DIR / "generator_main.py",
    "test-discriminator": GAN_DIR / "discriminator_main.py",
    "test-aes": BASE_DIR / "test_aes.py",
    "test-aes-esteg": BASE_DIR / "test_aes+esteg.py",
}

def run_script(script_path: Path) -> int:
    if not script_path.exists():
        print(f"[ERROR] No existe el archivo: {script_path}")
        return 1

    print(f"\n>>> Ejecutando: {script_path.name}\n")
    result = subprocess.run([sys.executable, str(script_path)])
    return result.returncode

def run_full_pipeline() -> int:
    steps = [
        "generate-v2",
        "test-aes-esteg",
    ]

    for step in steps:
        script_path = COMMANDS[step]
        code = run_script(script_path)
        if code != 0:
            print(f"\n[ERROR] Falló el paso: {step}")
            return code

    print("\n>>> Flujo completo ejecutado correctamente.")
    return 0

def main():
    parser = argparse.ArgumentParser(
        description="Runner del proyecto de GAN + criptografía + esteganografía"
    )
    parser.add_argument(
        "command",
        choices=[*COMMANDS.keys(), "full"],
        help="Comando a ejecutar",
    )

    args = parser.parse_args()

    if args.command == "full":
        sys.exit(run_full_pipeline())

    script_path = COMMANDS[args.command]
    sys.exit(run_script(script_path))

if __name__ == "__main__":
    main()