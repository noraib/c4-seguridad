import torch
import sys
import os
from torchvision.utils import save_image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.gan.Generator import Generator # Asegúrate de que la ruta sea correcta

# --- CONFIGURACIÓN ---
# Aquí puedes cambiar el nombre del checkpoint que quieras usar
CHECKPOINT = "generator_epoch_300.pth" 
MODEL_PATH = f"modelos/{CHECKPOINT}"
OUTPUT_DIR = "imagenes_esteganografia"
Z_DIM = 100
NUM_IMAGES = 50

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Cargar el Generador
# Nota: Asegúrate de que los parámetros de Generator() coincidan con el entrenamiento
netG = Generator(z_dim=Z_DIM).to(device)

# Cargar el archivo completo
checkpoint = torch.load(MODEL_PATH, map_location=device)

# Extraer solo la parte de los pesos (state_dict)
if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
    netG.load_state_dict(checkpoint["model_state_dict"])
    epoch = checkpoint.get('epoch', '300')
    print(f"✅ Pesos cargados correctamente desde el checkpoint de la época {epoch}")
else:
    netG.load_state_dict(checkpoint)
    print("✅ Pesos cargados directamente (formato simple)")

netG.eval()

# Generación
print(f"🚀 Generando {NUM_IMAGES} imágenes...")

with torch.no_grad():
    # 1. Creamos el ruido con forma (50, 100)
    # 50 es el número de imágenes, 100 es z_dim
    noise = torch.randn(NUM_IMAGES, Z_DIM, device=device)
    
    # 2. Pasamos el ruido por el generador
    fake_images = netG(noise)
    
    # 3. Desnormalizar y asegurar rango [0, 1]
    # Tu generador termina en Tanh(), por lo que devuelve valores entre [-1, 1]
    fake_images = (fake_images + 1) / 2.0
    fake_images = torch.clamp(fake_images, 0, 1)

    # 4. Guardar las imágenes
    for i in range(NUM_IMAGES):
        save_image(fake_images[i], os.path.join(OUTPUT_DIR, f'gen_{i+1:03d}.png'))

print(f"✨ ¡Hecho! Tienes tus imágenes listas en '{OUTPUT_DIR}' para aplicar LSB.")