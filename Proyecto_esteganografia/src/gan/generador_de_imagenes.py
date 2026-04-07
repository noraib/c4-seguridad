import torch
import os
from torchvision.utils import save_image
from src.gan.Generator import Generator # Asegúrate de que la ruta sea correcta

# --- CONFIGURACIÓN ---
# Aquí puedes cambiar el nombre del checkpoint que quieras usar
CHECKPOINT = "generator_epoch_50.pth" 
MODEL_PATH = f"modelos/{CHECKPOINT}"
OUTPUT_DIR = "imagenes_esteganografia"
Z_DIM = 100
NUM_IMAGES = 50

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Cargar el Generador
# Nota: Asegúrate de que los parámetros de Generator() coincidan con el entrenamiento
netG = Generator(z_dim=Z_DIM).to(device)

try:
    # map_location asegura que si el modelo se guardó en GPU, lo puedas abrir en CPU si hace falta
    state_dict = torch.load(MODEL_PATH, map_location=device)
    netG.load_state_dict(state_dict)
    netG.eval()
    print(f"✅ Modelo {CHECKPOINT} cargado con éxito.")
except FileNotFoundError:
    print(f"❌ Error: No se encuentra el archivo en {MODEL_PATH}")
    exit()

# 2. Generación
print(f"🚀 Generando {NUM_IMAGES} imágenes...")

with torch.no_grad():
    # Ruido latente
    noise = torch.randn(NUM_IMAGES, Z_DIM, 1, 1, device=device) # Ajusta si tu entrada no es (N, 100, 1, 1)
    fake_images = netG(noise)
    
    # Desnormalizar de [-1, 1] a [0, 1]
    fake_images = fake_images.clamp(-1, 1) # Por seguridad
    fake_images = (fake_images + 1) / 2.0

    for i in range(NUM_IMAGES):
        filename = os.path.join(OUTPUT_DIR, f'gen_{i+1:03d}.png')
        save_image(fake_images[i], filename)

print(f"✨ Imágenes guardadas en: {OUTPUT_DIR}")