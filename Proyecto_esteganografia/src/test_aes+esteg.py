from cripto.aes import generate_key, encrypt_message, decrypt_message
from esteganografia.lsb import encode_lsb, decode_lsb
from utils import select_file

def main():
    # mensaje y cifrado
    message = "Mensaje secreto"
    key = generate_key()
    encrypted = encrypt_message(message, key)
    
    # imagen ejemplo
    input_image = select_file("Selecciona la imagen base para ocultar el mensaje:")
    if not input_image:
        print("[!] Operación cancelada por el usuario.")
        return
    stego_image = "media_cripto_esteg/output/esteg_imagen.png"
    
    # insertar mensaje cifrado en la imagen
    encode_lsb(input_image, encrypted, stego_image)
    
    # extraer y descifrar
    extracted = decode_lsb(stego_image)
    decrypted = decrypt_message(extracted, key)
    
    print("Original:", message)
    print("Encriptado:", encrypted)
    print("Desencriptado:", decrypted)
    print("Mensaje extraido:", decrypted)


if __name__ == "__main__":
    main()