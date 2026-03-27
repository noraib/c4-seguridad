import torch
import torch.nn as nn

class Generator(nn.Module):
    def __init__(self, z_dim=100, img_channels=3, feature_map_size=64):
        super(Generator, self).__init__()

        # Parametros 
        self.z_dim = z_dim # Ruido
        self.img_channels = img_channels # Canales de la imagen (RGB)

        # PARTE 1: Fully Connected 
        # Empezamos con una imagen pequeña (4x4 pixeles)
        self.net = nn.Sequential(
            nn.Linear(self.z_dim, 512*4*4),
            nn.BatchNorm1d(512*4*4),
            nn.ReLU(True)
        )

        # PARTE 2: Upsampling con ConvTranspose2d
        # Vamos aumentando el tamaño de la imagen (el doble por cada salto)
        self.deconv_blocks = nn.Sequential(
            # Entrada: (512, 4, 4) -> Salida: (256, 8, 8)
            nn.ConvTranspose2d(512, 256, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(True),

            # Entrada: (256, 8, 8) -> Salida: (128, 16, 16)
            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(True),

            # Entrada: (128, 16, 16) -> Salida: (64, 32, 32)
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(True),

            # Entrada: (64, 32, 32) -> Salida: (img_channels, 64, 64)
            nn.ConvTranspose2d(64, self.img_channels, kernel_size=4, stride=2, padding=1),
            nn.Tanh()  # salida en [-1,1]
        )

    def forward(self, z):
        """
        z: tensor de ruido (batch_size, z_dim)
        """
        
        # Fully connected
        x = self.net(z)  # shape: (batch_size, 512*4*4)
        x = x.view(-1, 512, 4, 4)  # reshape para ConvTranspose2d

        # Upsampling
        img = self.deconv_blocks(x)  # shape: (batch_size, 3, 64, 64)
        return img











