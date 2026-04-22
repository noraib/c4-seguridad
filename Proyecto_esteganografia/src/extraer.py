# extraer.py
from tkinter import Tk, filedialog
from src.cripto.aes import decrypt_message
from src.esteganografia.lsb import decode_lsb
from src.utils import select_file

def main():
    print("--- EXTRAER MENSAJE ---")
    img_path = select_file("Selecciona la imagen con esteganografía")
    if not img_path: return

    hex_key = input("Introduce la clave (HEX): ").strip()
    key = bytes.fromhex(hex_key)

    try:
        extracted = decode_lsb(img_path)
        decrypted = decrypt_message(extracted, key)
        print(f"\n🔓 MENSAJE RECUPERADO: {decrypted}")
    except Exception as e:
        print(f"\n❌ Error: No se pudo descifrar. ¿La clave es correcta?")

if __name__ == "__main__":
    main()