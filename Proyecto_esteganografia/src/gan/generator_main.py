import matplotlib.pyplot as plt
import torch
import numpy as np
import os
from Generator import Generator  

os.makedirs("media_gan/generator", exist_ok=True)

# -------- PARÁMETROS --------
batch_size = 1         # por ahora generamos 1 imagen
z_dim = 100

# -------- RUIDO --------
z = torch.randn(batch_size, z_dim)

# -------- GENERADOR --------
G = Generator(z_dim=z_dim, img_channels=3)
G.eval()  # <--- importante para batch_size=1

# generar imagen
with torch.no_grad():  # evita calcular gradientes, más rápido y seguro
    fake_images = G(z)

# -------- GUARDAR IMAGEN --------
img = fake_images[0]                  # obtener imagen de tensor [1, 3, 64, 64]
img = (img + 1) / 2                   # [-1,1] -> [0,1]
img = img.permute(1, 2, 0)            # (Canales, Alto, Ancho) -> (Alto, Ancho, Canales)

plt.imshow(img)
plt.axis("off")
plt.savefig("media_gan/generator/resultado.png")
print("Imagen generada y guardada como resultado.png")