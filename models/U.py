import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision


class seg_head(nn.Module):
    def __init__(self, num_class=2):
        super().__init__()
        self.scale_4 = nn.Upsample(scale_factor=2)
        self.scale_3 = nn.Upsample(scale_factor=2)
        self.scale_2 = nn.Upsample(scale_factor=2)
        self.conv_4 =  nn.Conv2d(512, 256, kernel_size=(1,1), stride=(1,1))
        self.conv_3 =  nn.Conv2d(256, 128, kernel_size=(1,1), stride=(1,1))
        self.conv_2 =  nn.Conv2d(128, 64 , kernel_size=(1,1), stride=(1,1))

        self.conv = nn.Conv2d(64, 64, kernel_size=(1,1), stride=(1,1))
        self.BN_out = nn.BatchNorm2d(64)
        self.RELU6_out = nn.ReLU6()

        self.out = nn.Conv2d(64, num_class, kernel_size=(1,1), stride=(1,1))

    def forward(self, up4, up3, up2, up1):
        up2 = torchvision.ops.stochastic_depth(input=up2, p=0.5, mode='batch')
        up3 = torchvision.ops.stochastic_depth(input=up3, p=0.5, mode='batch')
        up4 = torchvision.ops.stochastic_depth(input=up4, p=0.5, mode='batch')
        up4 = self.scale_4(self.conv_4(up4))
        up3 = up3 + up4
        up3 = self.scale_3(self.conv_3(up3))
        up2 = up3 + up2
        up2 = self.scale_2(self.conv_2(up2))
        up = up2 + up1
        
        up = self.conv(up)
        up = self.BN_out(up)
        up = self.RELU6_out(up)
        up = self.out(up)

        return up

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
#         return self.double_conv(x)

class DoubleConv(nn.Module):
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



class U(nn.Module):
    def __init__(self, n_channels=3, n_classes=2, bilinear=False):
        super(U, self).__init__()
        self.n_channels = n_channels
        self.n_classes = n_classes
        self.bilinear = bilinear
        in_channels = 64
        self.inc = DoubleConv(n_channels, in_channels)
        self.down1 = Down(in_channels  , in_channels*2)
        self.down2 = Down(in_channels*2, in_channels*4)
        self.down3 = Down(in_channels*4, in_channels*8)
        factor = 2 if bilinear else 1
        self.down4 = Down(in_channels*8, (in_channels*16) // factor)
        self.up1 = Up(in_channels*16, in_channels*8  // factor, bilinear)
        self.up2 = Up(in_channels*8 , in_channels*4 // factor, bilinear)
        self.up3 = Up(in_channels*4 , (in_channels*2) // factor, bilinear)
        self.up4 = Up(in_channels*2 , in_channels , bilinear)
        # self.outc = OutConv(in_channels , n_classes)
        # self.sigmoid = torch.nn.Sigmoid()
        self.head = seg_head()

    def forward(self, x, teacher=False):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)
        up1 = self.up1(x5, x4)
        up2 = self.up2(up1, x3)
        up3 = self.up3(up2, x2)
        up4 = self.up4(up3, x1)
        # logits = self.outc(up4)
        logits = self.head(up4, up3, up2, up1)

        return logits

        # if self.training:
        #     return logits, up4, up3, up2, up1, x5, x4, x3, x2, x1
        # else:
        #     return logits
        
        # if self.training:
        #     return logits, up1, up2, up3, up4, x1, x2, x3, x4, x5
        # else:
        #     if teacher:
        #         return logits, up1, up2, up3, up4, x1, x2, x3, x4, x5
        #     else:
        #         return logits