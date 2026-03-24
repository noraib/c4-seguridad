import torch
import torch.nn as nn

class Discriminator(nn.Module):
    def __init__(self, img_channels=3, message_size=16):
        super(Discriminator, self).__init__()
        self.img_channels = img_channels
        self.message_size = message_size

        self.conv_blocks = nn.Sequential(
            nn.Conv2d(img_channels, 64, kernel_size=4, stride=2, padding=1),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Conv2d(128, 256, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Conv2d(256, 512, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True)
        )

        # Flatten
        self.flatten = nn.Flatten()

        # Cabeza Real/Falso
        self.fc_real_fake = nn.Sequential(
            nn.Linear(512*4*4, 1),
            nn.Sigmoid()
        )

        # Cabeza de decodificación de mensaje
        self.fc_message = nn.Sequential(
            nn.Linear(512*4*4, message_size),
            nn.Sigmoid()
        )

    def forward(self, img):
        x = self.conv_blocks(img)
        x = self.flatten(x)
        real_fake = self.fc_real_fake(x)
        message_hat = self.fc_message(x)
        return real_fake, message_hat