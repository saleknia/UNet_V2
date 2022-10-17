import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import math

class DoubleConv(nn.Module):
    """(convolution => [BN] => ReLU) * 2"""

    def __init__(self, in_channels, out_channels, mid_channels=None):
        super().__init__()
        if not mid_channels:
            mid_channels = out_channels
        self.double_conv = nn.Sequential(
            GhostModule(in_channels, mid_channels),
            GhostModule(mid_channels, out_channels),
        )

    def forward(self, x):
        x = self.double_conv(x)
        return x

class GhostModule(nn.Module):
    def __init__(self, inp, oup, kernel_size=3, ratio=10, dw_size=3, stride=1, relu=True):
        super(GhostModule, self).__init__()
        self.oup = oup
        init_channels = math.ceil(oup / ratio)
        new_channels = init_channels*(ratio-1)

        self.primary_conv = nn.Sequential(
            nn.Conv2d(inp, init_channels, kernel_size, stride, kernel_size//2, bias=False),
            nn.BatchNorm2d(init_channels),
            nn.ReLU(inplace=True) if relu else nn.Sequential(),
        )

        self.cheap_operation = nn.Sequential(
            nn.Conv2d(init_channels, new_channels, dw_size, stride, dw_size//2, groups=init_channels, bias=False),
            nn.BatchNorm2d(new_channels),
            nn.ReLU(inplace=True) if relu else nn.Sequential(),
        )

    def forward(self, x):
        x1 = self.primary_conv(x)
        x2 = self.cheap_operation(x1)
        out = torch.cat([x1,x2], dim=1)
        return out[:,:self.oup,:,:]

# class depthwise_separable_conv(nn.Module):
#  def __init__(self, nin, nout): 
#    super(depthwise_separable_conv, self).__init__() 
#    self.depthwise = nn.Conv2d(nin, nin , kernel_size=3, padding=1, groups=nin) 
#    self.pointwise = nn.Conv2d(nin, nout, kernel_size=1) 
  
#  def forward(self, x): 
#    out = self.depthwise(x) 
#    out = self.pointwise(out) 
#    return out

# class DoubleConv(nn.Module):
#     """(convolution => [BN] => ReLU) * 2"""

#     def __init__(self, in_channels, out_channels, mid_channels=None):
#         super().__init__()
#         if not mid_channels:
#             mid_channels = out_channels
#         self.double_conv = nn.Sequential(
#             depthwise_separable_conv(in_channels, mid_channels),
#             nn.BatchNorm2d(mid_channels),
#             nn.ReLU(inplace=True),
#             depthwise_separable_conv(mid_channels, out_channels),
#             nn.BatchNorm2d(out_channels),
#             nn.ReLU(inplace=True)
#         )

#     def forward(self, x):
#         x = self.double_conv(x)
#         return x

class DoubleConv_s(nn.Module):
    """(convolution => [BN] => ReLU) * 2"""

    def __init__(self, in_channels, out_channels, mid_channels=None):
        super().__init__()
        if not mid_channels:
            mid_channels = out_channels
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, mid_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(mid_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)

# class DoubleConv(nn.Module):
#     """(convolution => [BN] => ReLU) * 2"""

#     def __init__(self, in_channels, out_channels, mid_channels=None):
#         super().__init__()
#         int_in_channels = in_channels // 4
#         int_out_channels = out_channels // 4
        
#         self.double_conv = nn.Sequential(
#             nn.Conv2d(in_channels, int_in_channels, kernel_size=1, padding=0, bias=False),
#             nn.BatchNorm2d(int_in_channels),
#             nn.ReLU(inplace=True),
#             nn.Conv2d(int_in_channels, int_out_channels, kernel_size=3, padding=1, bias=False),
#             nn.BatchNorm2d(int_out_channels),
#             nn.ReLU(inplace=True),
#             nn.Conv2d(int_out_channels, int_out_channels, kernel_size=3, padding=1, bias=False),
#             nn.BatchNorm2d(int_out_channels),
#             nn.ReLU(inplace=True),
#             nn.Conv2d(int_out_channels, out_channels, kernel_size=1, padding=0, bias=False),
#             nn.BatchNorm2d(out_channels),
#             nn.ReLU(inplace=True),           
#         )

#     def forward(self, x):
#         return self.double_conv(x)


class Down(nn.Module):
    """Downscaling with maxpool then double conv"""

    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv(in_channels, out_channels)
        )

    def forward(self, x):
        return self.maxpool_conv(x)

class Up(nn.Module):
    """Upscaling then double conv"""

    def __init__(self, in_channels, out_channels, bilinear=True):
        super().__init__()

        # if bilinear, use the normal convolutions to reduce the number of channels
        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
            self.conv = DoubleConv(in_channels, out_channels, in_channels // 2)
        else:
            self.up = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
            self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x1, x2):
        x1 = self.up(x1)
        # input is CHW
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]

        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,
                        diffY // 2, diffY - diffY // 2])
        # if you have padding issues, see
        # https://github.com/HaiyongJiang/U-Net-Pytorch-Unstructured-Buggy/commit/0e854509c2cea854e247a9c615f175f76fbb2e3a
        # https://github.com/xiaopeng-liao/Pytorch-UNet/commit/8ebac70e633bac59fc22bb5195e513d5832fb3bd
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)

class OutConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(OutConv, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):
        return self.conv(x)

class U_loss(nn.Module):
    def __init__(self, n_channels=1, n_classes=9, bilinear=False):
        super(U_loss, self).__init__()
        self.n_channels = n_channels
        self.n_classes = n_classes
        self.bilinear = bilinear
        in_channels = 64
        self.inc = DoubleConv_s(n_channels, in_channels)
        self.down1 = Down(in_channels  , in_channels*2)
        self.down2 = Down(in_channels*2, in_channels*4)
        self.down3 = Down(in_channels*4, in_channels*8)
        factor = 2 if bilinear else 1
        self.down4 = Down(in_channels*8, (in_channels*16) // factor)
        self.up1 = Up(in_channels*16, in_channels*8  // factor, bilinear)
        self.up2 = Up(in_channels*8 , in_channels*4 // factor, bilinear)
        self.up3 = Up(in_channels*4 , (in_channels*2) // factor, bilinear)
        self.up4 = Up(in_channels*2 , in_channels , bilinear)
        self.outc = OutConv(in_channels , n_classes)

    def forward(self, x, multiple=False):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)
        up1 = self.up1(x5, x4)
        up2 = self.up2(up1, x3)
        up3 = self.up3(up2, x2)
        up4 = self.up4(up3, x1)
        logits = self.outc(up4)

        if multiple:
            return logits, up1, up2, up3, up4, x1, x2, x3, x4, x5
        else:
            return logits