import torch
import sys
import os
from torchvision.utils import save_image
from torchvision import utils

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.gan.Generator import Generator 

# --- CONFIGURACIÓN ---
CHECKPOINT = "gen_v2_epoch_650.pth" 
MODEL_PATH = f"modelos_v2_barcos/{CHECKPOINT}"
OUTPUT_DIR = "imagenes_esteganografia"
Z_DIM = 100
NUM_IMAGES = 50

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Instanciar y cargar
netG = Generator(z_dim=Z_DIM).to(device)
checkpoint = torch.load(MODEL_PATH, map_location=device)

# Manejar ambos formatos de guardado que tienes en tu código
if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
    netG.load_state_dict(checkpoint["model_state_dict"])
else:
    netG.load_state_dict(checkpoint)

# --- EL CAMBIO CLAVE ---
# Durante el entrenamiento NO usas .eval() antes de guardar las muestras.
# En DCGAN, BatchNorm a veces funciona mejor en .train() para generar.
netG.train() 

print(f"🚀 Generando imágenes...")

with torch.no_grad():
    # El ruido debe tener dimensiones (N, Z, 1, 1)
    noise = torch.randn(NUM_IMAGES, Z_DIM, 1, 1, device=device)
    
    fake_images = netG(noise)

    # Para que se vean IGUAL que en el entrenamiento:
    # Usamos la misma función y el mismo parámetro normalize=True
    for i in range(NUM_IMAGES):
        filename = os.path.join(OUTPUT_DIR, f'barco_gen_{i+1:03d}.png')
        
        # utils.save_image con normalize=True hace exactamente:
        # 1. Busca el min y max de la imagen
        # 2. Re-escala el rango [-1, 1] a [0, 1]
        utils.save_image(fake_images[i], filename, normalize=True)

print(f"✨ ¡Hecho! Ahora deberían verse idénticas a las de las épocas.")
# --- CONFIGURACIÓN ---
CHECKPOINT = "gen_v2_epoch_550.pth" 
MODEL_PATH = f"modelos_v2_barcos/{CHECKPOINT}"
OUTPUT_DIR = "imagenes_esteganografia"
Z_DIM = 100
NUM_IMAGES = 50

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Cargar el Generador
netG = Generator(z_dim=Z_DIM).to(device)

if not os.path.exists(MODEL_PATH):
    print(f"❌ Error: No se encuentra el archivo {MODEL_PATH}")
    sys.exit()

# Cargar el archivo con soporte para ambos formatos (el de dict y el de pesos directos)
checkpoint = torch.load(MODEL_PATH, map_location=device)

if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
    netG.load_state_dict(checkpoint["model_state_dict"])
    epoch = checkpoint.get('epoch', 'Desconocida')
    print(f"✅ Pesos cargados desde dict (Época {epoch})")
else:
    netG.load_state_dict(checkpoint)
    print("✅ Pesos cargados directamente (state_dict)")

netG.eval() # IMPORTANTE: Modo evaluación para BatchNorm

# --- GENERACIÓN ---
# PROBAR ESTO: Comenta .eval() y usa .train()
# netG.eval() 
netG.train() 

print(f"🚀 Generando {NUM_IMAGES} imágenes con corrección de contraste...")

with torch.no_grad():
    # Ruido (N, Z, 1, 1)
    noise = torch.randn(NUM_IMAGES, Z_DIM, 1, 1, device=device)
    
    # Generar
    fake_images = netG(noise)
    fake_images = fake_images.detach().cpu()

    for i in range(NUM_IMAGES):
        img = fake_images[i]
        
        # 1. Normalización Min-Max (lo que ya tenías)
        img_min = img.min()
        img_max = img.max()
        img = (img - img_min) / (img_max - img_min + 1e-5)
        
        # 2. NUEVO: Ajuste de Sigmoide para contraste (Curva S)
        # Esto oscurece los oscuros y aclara los claros, matando el gris.
        # El valor 10 controla la intensidad; puedes subirlo a 15 si sigue gris.
        img = torch.sigmoid(6 * (img - 0.5))
        
        filename = os.path.join(OUTPUT_DIR, f'barco_gen_{i+1:03d}.png')
        save_image(img, filename)

print(f"✨ ¡Hecho! Las imágenes deberían tener mucho más color ahora.")