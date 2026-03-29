# gan_steganography_train.py
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, utils
from torch.utils.data import DataLoader
import os

import Discriminator, Generator
# -----------------------------
# Configuración
# -----------------------------
device = 'cuda' if torch.cuda.is_available() else 'cpu'
batch_size = 64
z_dim = 100
num_epochs = 500
lr = 2e-4
model_dir = 'modelos'  # Carpeta de destino
samples_dir = 'muestras_entrenamiento' # Carpeta para ver progreso visual

# -----------------------------
# Función de Inicialización de Pesos (Para evitar imágenes borrosas)
# -----------------------------
def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        nn.init.normal_(m.weight.data, 0.0, 0.02)
    elif classname.find('BatchNorm') != -1:
        nn.init.normal_(m.weight.data, 1.0, 0.02)
        nn.init.constant_(m.bias.data, 0)

# -----------------------------
# Dataset
# -----------------------------
transform = transforms.Compose([
    transforms.Resize(64),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])

# 60,000 imágenes de 32x32 píxeles de 10 categorías (coches, aviones, pájaros...)
dataset = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

# -----------------------------
# Instanciar Generator y Discriminator
# -----------------------------
G = Generator.Generator(z_dim=z_dim, img_channels=3).to(device)
D = Discriminator.Discriminator(img_channels=3).to(device)

# Aplicar inicialización de pesos
G.apply(weights_init)
D.apply(weights_init)

# -----------------------------
# Optimizers y losses
# -----------------------------
optimizerG = optim.Adam(G.parameters(), lr=lr, betas=(0.5, 0.999))
optimizerD = optim.Adam(D.parameters(), lr=lr, betas=(0.5, 0.999))

# Learning Rate Decay (reduce el LR a la mitad cada 100 épocas)
schedulerG = optim.lr_scheduler.StepLR(optimizerG, step_size=100, gamma=0.5)
schedulerD = optim.lr_scheduler.StepLR(optimizerD, step_size=100, gamma=0.5)

criterion = nn.BCELoss()  # real/falso
fixed_noise = torch.randn(64, z_dim).to(device) # Ruido fijo para comparar evolución visual

os.makedirs(model_dir, exist_ok=True)
os.makedirs(samples_dir, exist_ok=True)

# -----------------------------
# Entrenamiento
# -----------------------------
print("Iniciando entrenamiento GAN balanceado...")

for epoch in range(num_epochs):
    for i, (real_images, _) in enumerate(dataloader):
        b_size = real_images.size(0)
        real_images = real_images.to(device)
        
        # Etiquetas con Label Smoothing (0.9 para ayudar al Generador)
        real_labels = torch.full((b_size, 1), 0.9, device=device)
        fake_labels = torch.zeros(b_size, 1).to(device)
        
        # ==========================================
        # 1. ENTRENAR DISCRIMINATOR
        # ==========================================
        D.zero_grad()
        
        # Real images
        out_real = D(real_images)
        loss_real = criterion(out_real, real_labels)
        
        # Fake images
        z = torch.randn(b_size, z_dim).to(device)
        fake_images = G(z)
        output_fake = D(fake_images.detach())
        loss_fake = criterion(output_fake, fake_labels)
        
        lossD = loss_real + loss_fake
        lossD.backward()
        optimizerD.step()
        
        # ==========================================
        # 2. ENTRENAR GENERATOR (PASO 1)
        # ==========================================
        G.zero_grad()
        # Para el generador usamos etiquetas de 1.0 porque su objetivo es engañar al 100%
        output_fake_for_G = D(fake_images) 
        lossG = criterion(output_fake_for_G, torch.ones(b_size, 1).to(device)) 
        lossG.backward()
        optimizerG.step()

        # ==========================================
        # 3. ENTRENAR GENERATOR (PASO 2 - Extra Boost)
        # ==========================================
        # Como el Discriminador es muy fuerte, entrenamos al Generador una 2da vez
        # por cada paso del Discriminador para equilibrar las fuerzas.
        z2 = torch.randn(b_size, z_dim).to(device)
        fake_images2 = G(z2)
        G.zero_grad()
        output_fake_for_G2 = D(fake_images2)
        lossG2 = criterion(output_fake_for_G2, torch.ones(b_size, 1).to(device))
        lossG2.backward()
        optimizerG.step()
        
        # Actualizamos la pérdida a mostrar para que refleje el último paso
        lossG = lossG2 
    
    # Actualizar Learning Rate cada época
    schedulerG.step()
    schedulerD.step()
    
    print(f"Epoch [{epoch+1}/{num_epochs}] Loss D: {lossD.item():.4f}, Loss G: {lossG.item():.4f} | LR: {optimizerG.param_groups[0]['lr']:.6f}")

    # -----------------------------
    # Guardado de Muestras y Checkpoints (Sin Early Stopping)
    # -----------------------------
    
    # Guardar muestra visual cada 10 épocas
    if (epoch + 1) % 10 == 0:
        with torch.no_grad():
            fake_display = G(fixed_noise)
            utils.save_image(fake_display, f'{samples_dir}/epoch_{epoch+1}.png', normalize=True)

    # Guardar checkpoint cada 50 épocas
    if (epoch + 1) % 50 == 0:
        path_cp = os.path.join(model_dir, f'generator_epoch_{epoch+1}.pth')
        torch.save(G.state_dict(), path_cp)
        print(f"  [+] Respaldo guardado: {path_cp}")
        
    # Guardar siempre la última época como "latest" para no perder progreso si cortas el script
    torch.save(G.state_dict(), os.path.join(model_dir, 'latest_generator.pth'))

# ---------------------------------------------------------
# GUARDAR VERSIÓN FINAL
# ---------------------------------------------------------
path_final = os.path.join(model_dir, 'final_gan_model.pth')
torch.save({
    'epoch': epoch,
    'g_state_dict': G.state_dict(),
    'd_state_dict': D.state_dict(),
    'lossG': lossG.item(),
    'lossD': lossD.item(),
    'optimizerG_state': optimizerG.state_dict(),
    'optimizerD_state': optimizerD.state_dict(),
}, path_final)

print("\nEntrenamiento finalizado exitosamente.")
print(f"- Carpeta de destino: {model_dir}/")
print(f"- Último Generador: latest_generator.pth")