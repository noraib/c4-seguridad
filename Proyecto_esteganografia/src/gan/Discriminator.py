import torch
import torch.nn as nn

class Discriminator(nn.Module):
    def __init__(self, img_channels=3):
        super(Discriminator, self).__init__()
        def critic_block(in_c, out_c, stride):
            return nn.Sequential(
                # Spectral Norm ayuda a que D no gane siempre
                nn.utils.spectral_norm(nn.Conv2d(in_c, out_c, 4, stride, 1, bias=False)),
                nn.LeakyReLU(0.2, inplace=True),
            )

        self.model = nn.Sequential(
            # 64x64 -> 32x32
            critic_block(img_channels, 64, 2),
            # 32x32 -> 16x16
            critic_block(64, 128, 2),
            # 16x16 -> 8x8
            critic_block(128, 256, 2),
            # 8x8 -> 4x4
            critic_block(256, 512, 2),
            # Salida final
            nn.Conv2d(512, 1, 4, 1, 0, bias=False),
            nn.Sigmoid()
        )

    def forward(self, img):
        return self.model(img).view(-1, 1)