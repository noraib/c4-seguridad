from PIL import Image
import os

def encode_lsb(image_path: str, message: bytes, output_path: str) -> None:
    """
    Inserta un mensaje (en bytes) en la imagen usando LSB.
    """
    # abrir imagen
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    img = Image.open(image_path)
    img = img.convert("RGB")
    pixels = list(img.getdata())
    
    # convertir mensaje a bits
    bits = ''.join(f"{byte:08b}" for byte in message)
    bits += '00000000'  # delimitador para fin de mensaje
    
    if len(bits) > len(pixels) * 3:
        raise ValueError("El mensaje es demasiado largo para la imagen")
    
    # insercion LSB
    new_pixels = []
    bit_idx = 0
    for r, g, b in pixels:
        r_new = r
        g_new = g
        b_new = b
        for color in range(3):
            if bit_idx < len(bits):
                if color == 0:
                    r_new = (r & ~1) | int(bits[bit_idx])
                elif color == 1:
                    g_new = (g & ~1) | int(bits[bit_idx])
                else:
                    b_new = (b & ~1) | int(bits[bit_idx])
                bit_idx += 1
        new_pixels.append((r_new, g_new, b_new))
    
    img.putdata(new_pixels)
    img.save(output_path)


def decode_lsb(image_path: str) -> bytes:
    """
    Extrae el mensaje oculto de la imagen usando LSB.
    """
    img = Image.open(image_path)
    img = img.convert("RGB")
    pixels = list(img.getdata())
    
    bits = ""
    for r, g, b in pixels:
        for color in (r, g, b):
            bits += str(color & 1)
    
    # agrupar en bytes
    message_bytes = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if byte == "00000000":
            break
        message_bytes.append(int(byte, 2))
    
    return bytes(message_bytes)