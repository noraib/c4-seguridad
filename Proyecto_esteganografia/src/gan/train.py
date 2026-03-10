import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from pathlib import Path
from generator import GeneratorMsg
from discriminator import DiscriminatorMsg
import numpy as np
import matplotlib.pyplot as plt

def train_steganogan(dataset_path, output_dir, msg_size=100, epochs=10, batch_size=32, lr=0.0002, device='cuda' if torch.cuda.is_available() else 'cpu'):
    device = torch.device(device)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # dataset
    transform = transforms.Compose([
        transforms.Resize((64,64)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))
    ])
    dataset = torchvision.datasets.ImageFolder(root=dataset_path, transform=transform)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # redes
    netG = GeneratorMsg(msg_size=msg_size).to(device)
    netD = DiscriminatorMsg(msg_size=msg_size).to(device)

    criterion_msg = nn.BCELoss()  # comparacion mensaje original vs decodificado

    optimizerG = optim.Adam(netG.parameters(), lr=lr, betas=(0.5,0.999))
    optimizerD = optim.Adam(netD.parameters(), lr=lr, betas=(0.5,0.999))

    print("Inicio de entrenamiento SteganoGAN...")

    for epoch in range(epochs):
        for i, (imgs, _) in enumerate(dataloader):
            imgs = imgs.to(device)

            B = imgs.size(0)
            # crear mensajes aleatorios binarios
            messages = torch.randint(0,2,(B,msg_size), dtype=torch.float).to(device)
            # generador
            netG.train()
            netD.eval()  # D no se actualiza mientras entrenamos G
            imgs_stego = netG(imgs, messages)

            messages_pred = netD(imgs_stego)
            lossG = criterion_msg(messages_pred, messages)
            optimizerG.zero_grad()
            lossG.backward()
            optimizerG.step()

            # discriminador
            netD.train()
            netG.eval()  # G no se actualiza mientras entrenamos D
            with torch.no_grad():
                imgs_stego = netG(imgs, messages)
            messages_pred = netD(imgs_stego)
            lossD = criterion_msg(messages_pred, messages)
            optimizerD.zero_grad()
            lossD.backward()
            optimizerD.step()

            if i % 20 == 0:
                print(f"[{epoch+1}/{epochs}] Batch {i}/{len(dataloader)} LossG: {lossG.item():.4f} LossD: {lossD.item():.4f}")

            # guardar imagen de ejemplo
            with torch.no_grad():
                # 1. Obtenemos un lote de imagenes real
                sample_imgs, _ = next(iter(dataloader))
                # 2. Limitamos a 8 unidades para la rejilla
                batch_limit = min(8, sample_imgs.size(0))
                z_imgs = sample_imgs[:batch_limit].to(device)
                
                # 3. Creamos mensajes que coincidan EXACTAMENTE con esa cantidad (batch_limit)
                z_msgs = torch.randint(0, 2, (batch_limit, msg_size)).float().to(device)
                
                # 4. El generador recibirá (8, 3, 64, 64) y (8, 100)
                stego_sample = netG(z_imgs, z_msgs)
            grid = torchvision.utils.make_grid(stego_sample, normalize=True, padding=2)
            plt.figure(figsize=(8,8))
            plt.axis('off')
            plt.title(f"Epoch {epoch+1}")
            plt.imshow(np.transpose(grid.cpu(), (1,2,0)))
            plt.savefig(Path(output_dir)/f"epoch_{epoch+1}.png")
            plt.close()

    torch.save(netG.state_dict(), Path(output_dir)/"generator_stegano.pth")
    torch.save(netD.state_dict(), Path(output_dir)/"discriminator_stegano.pth")
    print("Entrenamiento completado. Modelos guardados en", output_dir)
    
    
    
    
dataset_path = Path("data/dataset")  # con al menos una subcarpeta de imagenes, fake_class porque requiere
output_dir = Path("outputs/generated_images_stegano")

train_steganogan(dataset_path, output_dir, msg_size=100, epochs=50, batch_size=32)