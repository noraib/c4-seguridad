import torch
import torch.nn as nn

class Discriminator(nn.Module):
    def __init__(self, img_channels=3):
        super(Discriminator, self).__init__()
        self.img_channels = img_channels

        self.conv_blocks = nn.Sequential(
            # Entrada: (3, 64, 64) -> Salida: (64, 32, 32)
            nn.Conv2d(img_channels, 64, kernel_size=4, stride=2, padding=1),
            nn.LeakyReLU(0.2, inplace=True),

            # Entrada: (64, 32, 32) -> Salida: (128, 16, 16)
            nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),

            # Entrada: (128, 16, 16) -> Salida: (256, 8, 8)
            nn.Conv2d(128, 256, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),

            # Entrada: (256, 8, 8) -> Salida: (512, 4, 4)
            nn.Conv2d(256, 512, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True)
        )

        # Flatten
        self.flatten = nn.Flatten()

        # Cabeza Real/Falso
        self.fc_real_fake = nn.Sequential(
            # 512 canales * 4 alto * 4 ancho = 8192 neuronas de entrada
            nn.Linear(512*4*4, 1),
            nn.Sigmoid() # Devuelve una probabilidad entre 0 (falso) y 1 (real)
        )

    def forward(self, img):
        x = self.conv_blocks(img)
        x = self.flatten(x)
        real_fake = self.fc_real_fake(x)
        return real_fake