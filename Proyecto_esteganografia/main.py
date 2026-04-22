import subprocess
import sys
import os
from pathlib import Path
from src.proteger_csv import cambiar_estado_csv 
try:
    from tkinter import Tk, filedialog
except ImportError:
    print("Error: tkinter no está instalado.")
    print("Instálalo con: sudo apt install python3-tk")
    exit(1)

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
GAN_DIR = SRC_DIR / "gan"
PATH_CSV_REPORTE = "media_cripto_esteg/procesado_masivo/reporte_claves_final.csv"

# El diccionario de las opciones
OPTIONS = {
    "1": ("Generar imágenes con GAN", "script"),
    "2": ("Ocultar mensaje en imagen (Encriptar)", "script"),
    "3": ("Extraer mensaje de imagen (Desencriptar)", "script"),
    "4": ("Procesamiento masivo (CSV -> Imágenes + Keys)", "script"),
    "5": ("Caja Fuerte (Bloquear contenido/Desbloquear contenido/Obtener chiste)", "funcion"),
    "6": ("Salir", None), 
}

# Rutas para los scripts
SCRIPT_PATHS = {
    "1": GAN_DIR / "generador_de_imagenesV2.py",
    "2": SRC_DIR / "ocultar.py",
    "3": SRC_DIR / "extraer.py",
    "4": SRC_DIR / "procesador_masivo.py",
}


# bloquear / desbloquear csv
def menu_proteccion():
    print("\n" + "-"*30)
    print("   CAJA FUERTE DEL REPORTE")
    print("-"*30)
    print("1. Bloquear (Cifrar contenido)")
    print("2. Desbloquear (Descifrar contenido)")
    print("3. Obtener chiste")
    print("4. Volver atrás")
    
    op = input("\nSelecciona una opción: ")
    if op == "4": return

    pwd = input("Introduce la Contraseña Maestra: ")

    if op == "1":
        cambiar_estado_csv(PATH_CSV_REPORTE, pwd, "bloquear")
    elif op == "2":
        cambiar_estado_csv(PATH_CSV_REPORTE, pwd, "desbloquear")
    elif op == "3":
        cambiar_estado_csv(PATH_CSV_REPORTE, pwd, "obtener")
    else:
        print("Opción no válida.")

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

        if choice == "6":
            print("Saliendo... ¡Hasta pronto!")
            break

        if choice in OPTIONS:
            tipo = OPTIONS[choice][1]
            
            if tipo == "script":
                script_path = SCRIPT_PATHS[choice]
                run_script(script_path)
            elif tipo == "funcion":
                # Llama a la logica de cifrar/descifrar csv
                menu_proteccion()
        else:
            print("Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main()