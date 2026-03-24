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
initial_message_size = 16
num_epochs = 50
lambda_msg = 1.0  # peso de loss de mensaje
message_lengths = [4, 8, 16, 32]  # curriculum de mensajes

# -----------------------------
# Dataset
# -----------------------------
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])
dataset = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

# -----------------------------
# Instanciar Generator y Discriminator
# -----------------------------
# Asumimos que tus clases Generator y Discriminator ya están definidas
G = Generator(z_dim=z_dim, message_size=initial_message_size, img_channels=3).to(device)
D = Discriminator(message_size=initial_message_size).to(device)

# -----------------------------
# Optimizers y losses
# -----------------------------
optimizerG = optim.Adam(G.parameters(), lr=2e-4, betas=(0.5, 0.999))
optimizerD = optim.Adam(D.parameters(), lr=2e-4, betas=(0.5, 0.999))
criterion_gan = nn.BCELoss()  # real/falso
criterion_msg = nn.BCELoss()  # decodificación del mensaje

# -----------------------------
# Entrenamiento con curriculum de mensajes
# -----------------------------
curriculum_idx = 0
current_message_size = message_lengths[curriculum_idx]

for epoch in range(num_epochs):
    for real_images, _ in dataloader:
        batch_size_curr = real_images.size(0)
        real_images = real_images.to(device)
        
        # Mensajes aleatorios para el batch
        messages = torch.randint(0, 2, (batch_size_curr, current_message_size)).float().to(device)
        
        # --------------------
        # Entrenar Discriminator
        # --------------------
        D.zero_grad()
        real_labels = torch.ones(batch_size_curr, 1).to(device)
        fake_labels = torch.zeros(batch_size_curr, 1).to(device)
        
        # Real images
        out_real, _ = D(real_images)
        loss_real = criterion_gan(out_real, real_labels)
        
        # Fake images
        z = torch.randn(batch_size_curr, z_dim).to(device)
        fake_images = G(z, messages).detach()
        out_fake, _ = D(fake_images)
        loss_fake = criterion_gan(out_fake, fake_labels)
        
        lossD = loss_real + loss_fake
        lossD.backward()
        optimizerD.step()
        
        # --------------------
        # Entrenar Generator
        # --------------------
        G.zero_grad()
        z = torch.randn(batch_size_curr, z_dim).to(device)
        fake_images = G(z, messages)
        out_fake, message_hat = D(fake_images)
        
        loss_gan = criterion_gan(out_fake, real_labels)
        loss_msg = criterion_msg(message_hat, messages)
        lossG = loss_gan + lambda_msg * loss_msg
        lossG.backward()
        optimizerG.step()
    
    # --------------------
    # Evaluación del mensaje
    # --------------------
    with torch.no_grad():
        z_eval = torch.randn(batch_size, z_dim).to(device)
        messages_eval = torch.randint(0, 2, (batch_size, current_message_size)).float().to(device)
        fake_images_eval = G(z_eval, messages_eval)
        _, message_hat_eval = D(fake_images_eval)
        accuracy = (message_hat_eval.round() == messages_eval).float().mean()
        print(f"Epoch [{epoch+1}/{num_epochs}] | Message accuracy: {accuracy.item()*100:.2f}%")
    
    # --------------------
    # Curriculum de mensajes
    # --------------------
    if accuracy > 0.95 and curriculum_idx < len(message_lengths)-1:
        curriculum_idx += 1
        current_message_size = message_lengths[curriculum_idx]
        print(f"Incrementando longitud del mensaje a {current_message_size} bits")