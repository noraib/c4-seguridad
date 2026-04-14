import os
from tkinter import Tk, filedialog
from cripto.aes import generate_key, encrypt_message
from esteganografia.lsb import encode_lsb

def select_file():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(title="Selecciona la imagen base")
    root.destroy()
    return path

def main():
    print("--- OCULTAR MENSAJE ---")
    img_input = select_file()
    if not img_input: return

    message = input("Escribe el mensaje secreto: ")
    key = generate_key()
    
    encrypted = encrypt_message(message, key)
    output_path = "media_cripto_esteg/output/stego_result.png"
    
    encode_lsb(img_input, encrypted, output_path)
    
    print(f"\n✅ Proceso completado.")
    print(f"Imagen guardada en: {output_path}")
    print(f"CLAVE DE DESBLOQUEO (Guárdala!): {key.hex()}")

if __name__ == "__main__":
    main()