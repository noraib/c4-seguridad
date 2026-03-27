# gan_steganography_train.py
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import os

import Discriminator, Generator
# -----------------------------
# Configuración
# -----------------------------
device = 'cuda' if torch.cuda.is_available() else 'cpu'
batch_size = 64
z_dim = 100
num_epochs = 50
lr = 2e-4
patience = 5  # para Early Stopping
model_dir = 'modelos'  # Carpeta de destino

# -----------------------------
# Dataset
# -----------------------------
transform = transforms.Compose([
    transforms.Resize(64),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])

#60,000 imágenes de 32x32 píxeles de 10 categorías (coches, aviones, pájaros...)
dataset = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

# -----------------------------
# Instanciar Generator y Discriminator
# -----------------------------
# Asumimos que tus clases Generator y Discriminator ya están definidas
G = Generator.Generator(z_dim=z_dim, img_channels=3).to(device)
D = Discriminator.Discriminator(img_channels=3).to(device)

# -----------------------------
# Optimizers y losses
# -----------------------------
optimizerG = optim.Adam(G.parameters(), lr=lr, betas=(0.5, 0.999))
optimizerD = optim.Adam(D.parameters(), lr=lr, betas=(0.5, 0.999))
criterion = nn.BCELoss()  # real/falso

# -----------------------------
# Entrenamiento con curriculum de mensajes
# -----------------------------
for epoch in range(num_epochs):
    for i, (real_images, _) in enumerate(dataloader):
        b_size = real_images.size(0)
        real_images = real_images.to(device)
        
        # Etiquetas
        real_labels = torch.ones(b_size, 1).to(device)
        fake_labels = torch.zeros(b_size, 1).to(device)
        
        # --------------------
        # Entrenar Discriminator
        # --------------------
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
        
        # --------------------
        # Entrenar Generator
        # --------------------
        G.zero_grad()
        output_fake_for_G = D(fake_images) 
        lossG = criterion(output_fake_for_G, real_labels) 
        
        lossG.backward()
        optimizerG.step()
    
    print(f"Epoch [{epoch+1}/{num_epochs}] Loss D: {lossD.item():.4f}, Loss G: {lossG.item():.4f}")


    # -----------------------------
    # Checkpoint: mejor version
    # -----------------------------
    if lossG.item() < best_g_loss:
        best_g_loss = lossG.item()
        
        path_best = os.path.join(model_dir, 'best_generator.pth')
        torch.save(G.state_dict(), path_best)

        epochs_without_improvement = 0
        print(f"  --> Nueva mejor pérdida G: {best_g_loss:.4f}. Guardado 'best_generator.pth'")
    else:
        epochs_without_improvement += 1

    # -----------------------------
    # Early Stopping
    # -----------------------------
    if epochs_without_improvement >= patience:
        print(f"\n[!] Early Stopping en época {epoch+1}. La pérdida G no mejoró en {patience} épocas.")
        break

# ---------------------------------------------------------
# GUARDAR VERSIÓN FINAL (Al terminar o por Early Stopping)
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

print("\nEntrenamiento finalizado.")
print(f"- Carpeta de destino: {model_dir}/")
print(f"- Mejor Generador: best_generator.pth")
print(f"- Estado final: final_gan_model.pth")