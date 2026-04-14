import os
from pathlib import Path
from cripto.aes import generate_key, encrypt_message
from esteganografia.lsb import encode_lsb
from src.utils import select_file


def main():
    print("\n" + "─"*40)
    print("      OCULTAR MENSAJE")
    print("─"*40)
    
    img_input = select_file("Selecciona la imagen en la ventana que ha aparecido...")
    
    # --- Limpieza de rutas de WSL/Windows ---
    if img_input:
        img_input = img_input.replace("'", "").replace('"', "")
        if "wsl.localhost" in img_input:
            # Convierte la ruta de red de Windows a ruta local de Linux
            img_input = "/" + img_input.split("/Ubuntu/")[1] if "/Ubuntu/" in img_input else img_input

    if not img_input or not os.path.exists(img_input):
        print(f"❌ Error: No se seleccionó un archivo válido.")
        return

    message = input("[>] Escribe el mensaje secreto: ")
    if not message: return

    # Cifrado y Esteganografía
    key = generate_key()
    encrypted = encrypt_message(message, key)
    
    # Asegurar carpeta de salida
    output_dir = Path("media_cripto_esteg/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(output_dir / "stego_result.png")
    
    try:
        encode_lsb(img_input, encrypted, output_path)
        print(f"\n✅ ¡Mensaje oculto con éxito!")
        print(f"🖼️  Imagen generada: {output_path}")
        print(f"🔑 CLAVE HEXADECIMAL: {key.hex()}")
        print("\n¡Copia la clave! La necesitarás para la opción 3 del menú.")
    except Exception as e:
        print(f"❌ Error al procesar: {e}")

if __name__ == "__main__":
    main()