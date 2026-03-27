# gan_steganography_train.py
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

import Discriminator, Generator
# -----------------------------
# Configuración
# -----------------------------
device = 'cuda' if torch.cuda.is_available() else 'cpu'
batch_size = 64
z_dim = 100
num_epochs = 50
lr = 2e-4

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
G = Generator(z_dim=z_dim, img_channels=3).to(device)
D = Discriminator(img_channels=3).to(device)

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
