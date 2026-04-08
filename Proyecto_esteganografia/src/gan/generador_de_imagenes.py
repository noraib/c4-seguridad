import torch
import sys
import os
from torchvision.utils import save_image
from huggingface_hub import hf_hub_download

# Ajuste de ruta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.gan.Generator import Generator 

# --- CONFIGURACIÓN PARA V1 ---
REPO_ID = "Gonzatorra/Seguridad_BarcoV1_Epoch450" 
FILENAME = "generador_barco_epoch_450.pth" # Nombre exacto que descargó con éxito
OUTPUT_DIR = "imagenes_esteganografia"
Z_DIM = 100
NUM_IMAGES = 50

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Instanciar el Generador
netG = Generator(z_dim=Z_DIM).to(device)

# 2. Descarga desde Hugging Face
try:
    print(f"⏳ Obteniendo pesos de la V1...")
    model_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)
except Exception as e:
    print(f"❌ Error al descargar: {e}")
    sys.exit()

# 3. Cargar pesos
checkpoint = torch.load(model_path, map_location=device)
if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
    netG.load_state_dict(checkpoint["model_state_dict"])
else:
    netG.load_state_dict(checkpoint)

# IMPORTANTE: Para la V1, usa .eval() como hacías originalmente
netG.eval()
print(f"✅ Pesos de la V1 cargados y modelo en modo EVAL.")

# --- GENERACIÓN ---
print(f"🚀 Generando {NUM_IMAGES} imágenes...")

with torch.no_grad():
    # EL CAMBIO CLAVE PARA LA V1:
    # El ruido debe ser plano (N, Z_DIM), NO (N, Z_DIM, 1, 1)
    noise = torch.randn(NUM_IMAGES, Z_DIM, device=device)
    
    # Generar
    fake_images = netG(noise)
    
    # Desnormalizar: de [-1, 1] a [0, 1]
    fake_images = (fake_images + 1) / 2.0
    fake_images = torch.clamp(fake_images, 0, 1)

    # Guardar
    for i in range(NUM_IMAGES):
        filename = os.path.join(OUTPUT_DIR, f'barco_v1_{i+1:03d}.png')
        save_image(fake_images[i], filename)

print(f"✨ ¡Hecho! Imágenes generadas con éxito en '{OUTPUT_DIR}'")