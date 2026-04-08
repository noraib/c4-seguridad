import torch
import torch.nn as nn

class Discriminator(nn.Module):
    def __init__(self, img_channels=3):
        super(Discriminator, self).__init__()
        
        # Función auxiliar para crear bloques rápidamente
        def conv_block(in_f, out_f, stride=2, use_bn=True):
            layers = [
                # Usamos Spectral Norm para mayor estabilidad en texturas
                # Con esto, el discriminador se vuelve muy sensible a las inconsistencias
                # estructurales. Esto obliga al generador a crear imágenes extremadamente
                # coherentes.
                nn.utils.spectral_norm(nn.Conv2d(in_f, out_f, 4, stride, 1, bias=False))
            ]
            if use_bn:
                layers.append(nn.BatchNorm2d(out_f))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            layers.append(nn.Dropout(0.3))
            return nn.Sequential(*layers)

        self.model = nn.Sequential(
            # Entrada: (3, 64, 64) -> (64, 32, 32)
            conv_block(img_channels, 64, use_bn=False), # Primera capa sin BN
            
            # (64, 32, 32) -> (128, 16, 16)
            conv_block(64, 128),
            
            # (128, 16, 16) -> (256, 8, 8)
            conv_block(128, 256),
            
            # (256, 8, 8) -> (512, 4, 4)
            conv_block(256, 512),
            
            # Capa final de decisión
            nn.Conv2d(512, 1, kernel_size=4, stride=1, padding=0, bias=False),
            # Salida: (1, 1, 1) -> Un solo valor por imagen
        )

    def forward(self, x):
        return self.model(x).view(-1, 1) # Retorna (Batch, 1)