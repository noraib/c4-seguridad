import torch
import torch.nn as nn

class Generator(nn.Module):
    def __init__(self, z_dim=100, message_size=128, img_channels=3, feature_map_size=64):
        super(Generator, self).__init__()

        # Parametros 
        self.z_dim = z_dim # Ruido
        self.message_size = message_size # Bits del mensaje oculto
        self.input_dim = z_dim + message_size  # Concatenamos z (ruido) + mensaje
        self.img_channels = img_channels
        self.feature_map_size = feature_map_size

        # PARTE 1: Fully Connected 
        # Empezamos con una imagen pequeña (4x4 pixeles)
        self.net = nn.Sequential(
            # z+m -> 4x4x512
            nn.Linear(self.input_dim, 512*4*4),
            nn.BatchNorm1d(512*4*4),
            nn.ReLU(True)
        )

        # PARTE 2: Upsampling con ConvTranspose2d
        # Vamos aumentando el tamaño de la imagen (el doble por cada salto)
        self.deconv_blocks = nn.Sequential(
            nn.ConvTranspose2d(512, 256, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(True),

            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(True),

            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(True),

            nn.ConvTranspose2d(64, self.img_channels, kernel_size=4, stride=2, padding=1),
            nn.Tanh()  # salida en [-1,1]
        )

    def forward(self, z, message):
        """
        z: tensor de ruido (batch_size, z_dim)
        message: tensor binario (batch_size, message_size)
        """
        # Concatenamos z + message
        x = torch.cat([z, message], dim=1)  # shape: (batch_size, z_dim+message_size)

        # Fully connected
        x = self.net(x)  # shape: (batch_size, 512*4*4)
        x = x.view(-1, 512, 4, 4)  # reshape para ConvTranspose2d

        # Upsampling
        img = self.deconv_blocks(x)  # shape: (batch_size, 3, 64, 64)
        return img











