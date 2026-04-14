import torch
import torch.nn as nn

class Generator(nn.Module):
    def __init__(self, z_dim=100, img_channels=3):
        super(Generator, self).__init__()
        
        # Comvertimos el vector de ruido z en un mapa de características inicial de 4x4
        # Es como crear una imagen muy pequeña a partir del ruido, que luego se irá ampliando
        # Esta imagen pequeña tiene 512 canales, lo que le da mucha capacidad para representar
        # información compleja
        self.init_size = 4 
        self.l1 = nn.Sequential(nn.Linear(z_dim, 512 * self.init_size**2))

        self.conv_blocks = nn.Sequential(
            nn.BatchNorm2d(512),
            # Bloque 1: De 4x4 a 8x8 (duplicamos el tamaño y reducimos los canales a la mitad)
            nn.Upsample(scale_factor=2),
            nn.Conv2d(512, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256, 0.8),
            nn.LeakyReLU(0.2, inplace=True),

            # Bloque 2: De 8x8 a 16x16
            # Seguimos ampliando la imagen y reduciendo los canales para que el modelo se
            # enfoque en detalles más específicos
            nn.Upsample(scale_factor=2),
            nn.Conv2d(256, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128, 0.8),
            nn.LeakyReLU(0.2, inplace=True),

            # Bloque 3: De 16x16 a 32x32
            nn.Upsample(scale_factor=2),
            nn.Conv2d(128, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64, 0.8),
            nn.LeakyReLU(0.2, inplace=True),

            # Bloque 4: De 32x32 a 64x64
            nn.Upsample(scale_factor=2),
            # Finalmente, convertimos a la imagen de salida con el número correcto de canales
            # (3 para RGB) y una imagen de 64x64 píxeles
            nn.Conv2d(64, img_channels, kernel_size=3, stride=1, padding=1),
            nn.Tanh()
        )

    def forward(self, z):
        out = self.l1(z)
        # Transformamos el vector de salida de la capa lineal en un mapa de características
        # con 512 canales y tamaño 4x4
        out = out.view(out.shape[0], 512, self.init_size, self.init_size)
        img = self.conv_blocks(out)
        return img