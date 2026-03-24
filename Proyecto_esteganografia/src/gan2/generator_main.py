import matplotlib.pyplot as plt
import torch
import numpy as np
from Generator import Generator  # asegúrate de que la ruta sea correcta

# -------- PARÁMETROS --------
batch_size = 1         # por ahora generamos 1 imagen
z_dim = 100
message_size = 128     # puede contener hasta 128 bits (~16 caracteres)

# -------- MENSAJE --------
texto = "SOS"                     # tu mensaje
texto_bytes = texto.encode("utf-8")         # convierte a bytes
mensaje_bits = np.unpackbits(np.frombuffer(texto_bytes, dtype=np.uint8))  # bits

# rellenar a message_size si es más corto
mensaje_bits = np.pad(mensaje_bits, (0, message_size - len(mensaje_bits)))

# convertir a tensor y batch
message_tensor = torch.tensor(mensaje_bits, dtype=torch.float32).unsqueeze(0)

# -------- RUIDO --------
z = torch.randn(batch_size, z_dim)

# -------- GENERADOR --------
G = Generator(z_dim=z_dim, message_size=message_size)
G.eval()  # <--- importante para batch_size=1

# generar imagen
with torch.no_grad():  # evita calcular gradientes, más rápido y seguro
    fake_images = G(z, message_tensor)

# -------- GUARDAR IMAGEN --------
img = fake_images[0].detach()
img = (img + 1) / 2                   # [-1,1] -> [0,1]
img = img.permute(1, 2, 0)            # C,H,W -> H,W,C

plt.imshow(img)
plt.axis("off")
plt.savefig("resultado.png")
print("Imagen generada y guardada como resultado.png")