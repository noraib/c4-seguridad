from PIL import Image
import torch
from torchvision import transforms
from Discriminator import Discriminator  # asegúrate de que el archivo se llame Discriminator.py

# -------- PARÁMETROS --------
batch_size = 1
img_channels = 3

# -------- ENTRADA (IMAGEN) --------
ruta_imagen = "media_gan/generator/resultado.png"

# -------- CARGAR Y TRANSFORMAR IMAGEN --------
transform = transforms.Compose([
    transforms.Resize((64, 64)),                # Asegura que sea 64x64
    transforms.ToTensor(),                      # Convierte a tensor [0, 1] y cambia a (C, H, W)
    transforms.Normalize([0.5], [0.5])          # Pasa de [0, 1] a [-1, 1] (opuesto al generador)
])

# Abrimos la imagen con PIL y aplicamos la transformación
img_pil = Image.open(ruta_imagen).convert('RGB')
input_image = transform(img_pil)                # Resultado: Tensor [3, 64, 64]
input_image = input_image.unsqueeze(0)          # Añadimos el batch: [1, 3, 64, 64]

# -------- DISCRIMINADOR --------
D = Discriminator(img_channels=img_channels)
D.eval()  

# clasificar imagen
with torch.no_grad():
    # El discriminador nos devuelve un valor entre 0 y 1 
    prediction = D(input_image)

# -------- MOSTRAR RESULTADO --------
probabilidad_real = prediction.item()

print(f"Resultado del Discriminador: {probabilidad_real:.4f}")

if probabilidad_real > 0.5:
    print("El modelo cree que la imagen es REAL.")
else:
    print("El modelo cree que la imagen es FALSA / RUIDO.")