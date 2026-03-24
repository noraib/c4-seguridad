import torch
import torch.nn as nn

class Generator(nn.Module):
    def __init__(self, z_dim=100, message_size=16, img_channels=3, feature_map_size=64):
        super(Generator, self).__init__()
        self.z_dim = z_dim
        self.message_size = message_size
        self.input_dim = z_dim + message_size  # concatenamos z + mensaje
        self.img_channels = img_channels
        self.feature_map_size = feature_map_size

        self.net = nn.Sequential(
            # Fully connected: z+m -> 4x4x512
            nn.Linear(self.input_dim, 512*4*4),
            nn.BatchNorm1d(512*4*4),
            nn.ReLU(True)
        )

        # Upsampling con ConvTranspose2d
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

# Ejemplo de uso
batch_size = 16
z_dim = 100
message_size = 16

z = torch.randn(batch_size, z_dim)
message = torch.randint(0, 2, (batch_size, message_size)).float()  # mensajes binarios

G = Generator(z_dim=z_dim, message_size=message_size)
fake_images = G(z, message)
print(fake_images.shape)  # (16, 3, 64, 64)