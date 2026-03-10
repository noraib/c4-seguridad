import torch
import torch.nn as nn

class DiscriminatorMsg(nn.Module):
    """
    Discriminador que intenta recuperar el mensaje de la imagen
    """
    def __init__(self, msg_size=100, nc=3, ndf=64):
        super(DiscriminatorMsg, self).__init__()
        self.msg_size = msg_size
        self.main = nn.Sequential(
            nn.Conv2d(nc, ndf, 3, 1, 1),
            nn.ReLU(True),
            nn.Conv2d(ndf, ndf, 3, 1, 1),
            nn.ReLU(True),
            nn.Conv2d(ndf, ndf, 3, 1, 1),
            nn.ReLU(True),
        )
        self.fc = nn.Linear(ndf*64*64, msg_size)

    def forward(self, img):
        B, C, H, W = img.shape
        x = self.main(img)
        x = x.view(B, -1)
        out = torch.sigmoid(self.fc(x))  # salida en 0-1 para mensaje binario
        return out