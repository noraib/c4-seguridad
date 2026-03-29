import torch
import os
from torchvision.utils import save_image
from Generator import Generator

# Configuración
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model_path = 'modelos/latest_generator.pth'
output_dir = 'imagenes_generadas'
os.makedirs(output_dir, exist_ok=True)

# Cargar Modelo
z_dim = 100
netG = Generator(z_dim=z_dim).to(device)
netG.load_state_dict(torch.load(model_path, map_location=device))
netG.eval()

print(f"Generando 50 imágenes desde {model_path}...")

with torch.no_grad():
    # Generamos 50 vectores de ruido aleatorio
    noise = torch.randn(50, z_dim).to(device)
    fake_images = netG(noise)
    
    # Desnormalizar de [-1, 1] a [0, 1] para guardar como imagen
    fake_images = (fake_images + 1) / 2.0

    for i in range(50):
        save_image(fake_images[i], os.path.join(output_dir, f'img_{i+1}.png'))

print(f"Hecho. Imágenes guardadas en: {output_dir}")