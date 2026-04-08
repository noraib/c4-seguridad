import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, utils
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
import os

# Importamos tus clases
from Discriminator import Discriminator 
from Generator import Generator

# 1. Inicialización de pesos
def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        nn.init.normal_(m.weight.data, 0.0, 0.02)
    elif classname.find('BatchNorm') != -1:
        nn.init.normal_(m.weight.data, 1.0, 0.02)
        nn.init.constant_(m.bias.data, 0)

# Configuración
device = "cuda" if torch.cuda.is_available() else "cpu"
z_dim = 100
batch_size = 64 
lr = 0.0002
num_epochs = 500
model_dir = 'modelos_v2_barcos'
samples_dir = 'muestras_entrenamiento_barcos_v2'

writer = SummaryWriter("runs/gan_barcos_v2")
os.makedirs(model_dir, exist_ok=True)
os.makedirs(samples_dir, exist_ok=True)

# Dataset Barcos
transform = transforms.Compose([
    transforms.Resize(64),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

full_dataset = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
ship_indices = [i for i, (_, label) in enumerate(full_dataset) if label == 8]
ship_dataset = torch.utils.data.Subset(full_dataset, ship_indices)
dataloader = DataLoader(ship_dataset, batch_size=batch_size, shuffle=True)

# Instanciar modelos y aplicar pesos
netG = Generator(z_dim).to(device)
netD = Discriminator().to(device)
netG.apply(weights_init)
netD.apply(weights_init)

optimizerG = optim.Adam(netG.parameters(), lr=lr, betas=(0.5, 0.999))
optimizerD = optim.Adam(netD.parameters(), lr=lr, betas=(0.5, 0.999))
criterion = nn.BCELoss()

# RUIDO FIJO: Necesitamos 64 para el de disco (8x8)
fixed_noise = torch.randn(64, z_dim, 1, 1, device=device)

print(f"Entrenamiento V2 (Barcos) iniciado.")


starting_epoch = 500  # Empezamos desde donde lo dejaste
new_total_epochs = 700 # Entrenaremos 200 épocas más
# Bajamos el LR para no romper el modelo (Fine-tuning suave)
lr_finetune = 0.00005 

# 1. Cargar pesos del Generador de la época 500
path_checkpoint = os.path.join(model_dir, 'gen_v2_epoch_500.pth')

if os.path.exists(path_checkpoint):
    checkpoint = torch.load(path_checkpoint, map_location=device)
    
    # Intentamos cargar asumiendo que es un diccionario o solo el state_dict
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        netG.load_state_dict(checkpoint['model_state_dict'])
        print(" >>> Checkpoint cargado desde diccionario ('model_state_dict').")
    else:
        # Si falla lo anterior, es que guardaste el state_dict directamente
        netG.load_state_dict(checkpoint)
        print(" >>> Checkpoint cargado directamente (state_dict).")
else:
    print(f" !!! No se encontró el archivo en {path_checkpoint}.")
# 2. Re-instanciar optimizadores con el nuevo LR bajo
optimizerG = optim.Adam(netG.parameters(), lr=lr_finetune, betas=(0.5, 0.999))
optimizerD = optim.Adam(netD.parameters(), lr=lr_finetune, betas=(0.5, 0.999))

for epoch in range(starting_epoch, new_total_epochs):
    epoch_idx = epoch + 1
    
    for i, (real_images, _) in enumerate(dataloader):
        b_size = real_images.size(0)
        real_images = real_images.to(device)
        
        # --- Discriminador ---
        optimizerD.zero_grad()
        label_real = torch.full((b_size, 1), 0.9, device=device)
        label_fake = torch.zeros(b_size, 1).to(device)
        
        out_real = netD(real_images)
        loss_D_real = criterion(out_real, label_real)
        
        z = torch.randn(b_size, z_dim, 1, 1, device=device)
        fake_images = netG(z)
        out_fake = netD(fake_images.detach())
        loss_D_fake = criterion(out_fake, label_fake) 
        
        lossD = (loss_D_real + loss_D_fake) / 2
        lossD.backward()
        optimizerD.step()
        
        # --- Generador ---
        netG.zero_grad()
        out_g = netD(fake_images) 
        lossG = criterion(out_g, torch.ones(b_size, 1).to(device)) 
        lossG.backward()
        optimizerG.step()

        if i % 100 == 0:
            step = epoch * len(dataloader) + i
            writer.add_scalar('Loss/Discriminador', lossD.item(), step)
            writer.add_scalar('Loss/Generador', lossG.item(), step)

    # --- FINAL DE LA ÉPOCA ---
    with torch.no_grad():
        fake_all = netG(fixed_noise)
        
        # 1. TENSORBOARD: Grid de 8x2 (16 imágenes)
        # nrow=8 pone 8 columnas, por lo que 16/8 = 2 filas.
        grid_tb = utils.make_grid(fake_all[:16], nrow=8, normalize=True)
        writer.add_image('Muestras/Generadas', grid_tb, epoch_idx)
        
        # 2. DISCO: Cada 50 épocas guardar Grid 8x8 (64 imágenes)
        if epoch_idx % 50 == 0:
            utils.save_image(
                fake_all, 
                f'{samples_dir}/barco_v2_grid_8x8_epoch_{epoch_idx}.png', 
                nrow=8, 
                normalize=True
            )
            print(f" >>> Muestra 8x8 guardada en disco (Época {epoch_idx})")

    # Checkpoints
    torch.save(netG.state_dict(), os.path.join(model_dir, 'generator_v2_latest.pth'))
    
    if epoch_idx % 50 == 0:
        torch.save(netG.state_dict(), os.path.join(model_dir, f'gen_v2_epoch_{epoch_idx}.pth'))
        print(f" >>> Checkpoint {epoch_idx} guardado.")

    print(f"Época [{epoch_idx}/{num_epochs}] Loss D: {lossD.item():.4f} | Loss G: {lossG.item():.4f}")

writer.close()