import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, utils
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
import os

# Importamos tus clases desde los archivos correspondientes
from Discriminator import Discriminator 
from Generator import Generator

# -----------------------------
# 1. Configuración de Parámetros
# -----------------------------
device = 'cuda' if torch.cuda.is_available() else 'cpu'
batch_size = 64
z_dim = 100
num_epochs = 500
lr = 2e-4
model_dir = 'modelos'
samples_dir = 'muestras_entrenamiento_barcos'

# Inicializar TensorBoard (para ver gráficas en localhost:6006)
writer = SummaryWriter('runs/gan_barcos_v1')

os.makedirs(model_dir, exist_ok=True)
os.makedirs(samples_dir, exist_ok=True)

# -----------------------------
# 2. Inicialización de Pesos
# -----------------------------
def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        nn.init.normal_(m.weight.data, 0.0, 0.02)
    elif classname.find('BatchNorm') != -1:
        nn.init.normal_(m.weight.data, 1.0, 0.02)
        nn.init.constant_(m.bias.data, 0)

# -----------------------------
# 3. Preparación del Dataset (SOLO BARCOS)
# -----------------------------
transform = transforms.Compose([
    transforms.Resize(64),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3) # Normalización a [-1, 1] para Tanh
])

# Cargamos el dataset completo
full_dataset = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)

# Filtramos por la clase 8 (Barcos)
ship_indices = [i for i, (_, label) in enumerate(full_dataset) if label == 8]
ship_dataset = torch.utils.data.Subset(full_dataset, ship_indices)

# Cargador de datos con la clase filtrada
dataloader = DataLoader(ship_dataset, batch_size=batch_size, shuffle=True)

print(f"Entrenamiento configurado solo para BARCOS (Clase 8).")
print(f"Total de imágenes de entrenamiento: {len(ship_dataset)}")
# -----------------------------
# 4. Instanciar Modelos
# -----------------------------
G = Generator(z_dim=z_dim, img_channels=3).to(device)
D = Discriminator(img_channels=3).to(device)

G.apply(weights_init)
D.apply(weights_init)

# -----------------------------
# 5. Optimización y Pérdida
# -----------------------------
optimizerG = optim.Adam(G.parameters(), lr=lr, betas=(0.5, 0.999))
optimizerD = optim.Adam(D.parameters(), lr=lr, betas=(0.5, 0.999))

# BCEWithLogitsLoss es necesaria porque el Discriminador no tiene Sigmoid final
criterion = nn.BCEWithLogitsLoss() 

fixed_noise = torch.randn(64, z_dim).to(device)

# -----------------------------
# 6. Bucle de Entrenamiento
# -----------------------------
print(f"Entrenamiento iniciado en {device}.")
print("Ejecuta 'tensorboard --logdir=runs' en otra terminal para ver el progreso.")

for epoch in range(num_epochs):
    for i, (real_images, _) in enumerate(dataloader):
        b_size = real_images.size(0)
        real_images = real_images.to(device)
        
        # Etiquetas con Soft labels (0.9 para reales) para estabilizar
        real_labels = torch.full((b_size, 1), 0.9, device=device)
        fake_labels = torch.zeros(b_size, 1).to(device)
        
        # --- PARÁMETRO 1: Entrenar Discriminador ---
        D.zero_grad()
        
        # Loss con imágenes reales
        out_real = D(real_images)
        loss_D_real = criterion(out_real, real_labels)
        
        # Loss con imágenes falsas
        z = torch.randn(b_size, z_dim, device=device)
        fake_images = G(z)
        out_fake = D(fake_images.detach()) # .detach() para no entrenar G aquí
        loss_D_fake = criterion(out_fake, fake_labels)
        
        lossD = loss_D_real + loss_D_fake
        lossD.backward()
        optimizerD.step()
        
        # --- PARÁMETRO 2: Entrenar Generador (1:1) ---
        G.zero_grad()
        
        # El Generador quiere que D clasifique sus imágenes como Reales (1.0)
        out_g = D(fake_images) 
        lossG = criterion(out_g, torch.ones(b_size, 1).to(device)) 
        
        lossG.backward()
        optimizerG.step()

        # Enviar métricas a TensorBoard cada 100 pasos
        if i % 100 == 0:
            step = epoch * len(dataloader) + i
            writer.add_scalar('Loss/Discriminador', lossD.item(), step)
            writer.add_scalar('Loss/Generador', lossG.item(), step)

    # --- FINAL DE LA ÉPOCA ---

    # Visualización de progreso
    with torch.no_grad():
        fake_display = G(fixed_noise)
        grid = utils.make_grid(fake_display[:16], normalize=True)
        writer.add_image('Muestras/Generadas', grid, epoch)
        
        # Guardar imagen en carpeta cada 10 épocas
        if (epoch + 1) % 10 == 0:
            utils.save_image(fake_display, f'{samples_dir}/barco_epoch_{epoch+1}.png', normalize=True)

    # GUARDADO DE CHECKPOINTS (Tu sistema de seguridad)
    
    # 1. El último estado (siempre se sobreescribe)
    torch.save(G.state_dict(), os.path.join(model_dir, 'generator_ship_latest.pth'))
    
    # 2. Checkpoint Histórico (Cada 50 épocas, no se sobreescribe)
    if (epoch + 1) % 50 == 0:
        cp_name = f'generador_barco_epoch_{epoch+1}.pth'
        torch.save({
            'epoch': epoch + 1,
            'model_state_dict': G.state_dict(),
            'optimizer_state_dict': optimizerG.state_dict(),
            'lossG': lossG.item()
        }, os.path.join(model_dir, cp_name))
        print(f" >>> Checkpoint histórico guardado: {cp_name}")

    print(f"Época [{epoch+1}/{num_epochs}] Loss D: {lossD.item():.4f} | Loss G: {lossG.item():.4f}")

writer.close()
print("Proceso finalizado. El mejor modelo será aquel donde las texturas sean más naturales.")