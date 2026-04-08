import torch
import sys
import os
from torchvision.utils import save_image
from huggingface_hub import hf_hub_download

# 1. Ajuste de ruta para importar tu clase Generator
# Asegúrate de que tus compañeros tengan el archivo Generator.py en la ruta correcta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
try:
    from src.gan.GeneratorV2 import GeneratorV2 as Generator 
except ImportError:
    print("❌ Error: No se pudo encontrar Generator.py. Asegúrate de que la estructura de carpetas es correcta.")
    sys.exit()

# --- CONFIGURACIÓN DE TU REPOSITORIO ---
REPO_ID = "Gonzatorra/Seguridad_BarcoV2_Epoch550" 
FILENAME = "gen_v2_epoch_550.pth"

# --- CONFIGURACIÓN DE SALIDA ---
OUTPUT_DIR = "imagenes_esteganografia"
Z_DIM = 100
NUM_IMAGES = 50

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. DESCARGA AUTOMÁTICA
try:
    print(f"⏳ Descargando pesos desde Hugging Face ({REPO_ID})...")
    model_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)
except Exception as e:
    print(f"❌ Error al conectar con Hugging Face: {e}")
    sys.exit()

# 3. CARGAR EL MODELO
netG = Generator(z_dim=Z_DIM).to(device)
checkpoint = torch.load(model_path, map_location=device)

# Tu entrenamiento guarda el state_dict directamente, así que lo cargamos así:
if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
    netG.load_state_dict(checkpoint["model_state_dict"])
else:
    netG.load_state_dict(checkpoint)

# 4. GENERACIÓN (Modo train para evitar el gris)
netG.train() 

print(f"🚀 Generando {NUM_IMAGES} barcos para esteganografía...")

with torch.no_grad():
    noise = torch.randn(NUM_IMAGES, Z_DIM, 1, 1, device=device)
    fake_images = netG(noise).detach().cpu()

    for i in range(NUM_IMAGES):
        img = fake_images[i]
        
        # Corrección de contraste (Min-Max)
        img_min = img.min()
        img_max = img.max()
        img = (img - img_min) / (img_max - img_min + 1e-5)
        
        # Curva de contraste para evitar imágenes lavadas
        img = torch.sigmoid(8 * (img - 0.5))
        
        filename = os.path.join(OUTPUT_DIR, f'barco_gen_{i+1:03d}.png')
        save_image(img, filename)

print(f"✨ ¡Hecho! Tus compañeros ya tienen los barcos en la carpeta '{OUTPUT_DIR}'")