import torch
import torch.nn as nn

class GeneratorMsg(nn.Module):
    """
    Generador que recibe imagen + mensaje (vector) y genera imagen con mensaje oculto
    """
    def __init__(self, msg_size=100, nc=3, ngf=64):
        super(GeneratorMsg, self).__init__()
        self.msg_size = msg_size

        # codificador de mensaje a tensor
        self.msg_fc = nn.Linear(msg_size, 64*64*1)

        # convolucion para fusionar mensaje y imagen
        self.main = nn.Sequential(
            nn.Conv2d(nc+1, ngf, 3, 1, 1),
            nn.ReLU(True),
            nn.Conv2d(ngf, ngf, 3, 1, 1),
            nn.ReLU(True),
            nn.Conv2d(ngf, nc, 3, 1, 1),
            nn.Tanh()
        )

    def forward(self, img, msg):
        """
        img: (B,3,H,W) imagen original normalizada -1 a 1
        msg: (B, msg_size) vector binario del mensaje
        """
        B, C, H, W = img.shape
        # expandir mensaje
        msg_encoded = self.msg_fc(msg)  # (B, H*W*1)
        msg_encoded = msg_encoded.view(B, 1, H, W)  # (B,1,H,W)

        # concatenar imagen + mensaje
        x = torch.cat([img, msg_encoded], dim=1)
        out = self.main(x)
        return out