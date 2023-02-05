import math
import torch
import torch.nn as nn
import torchvision
import torch.nn.functional as F
import einops
import timm
from torchvision import models as resnet_model
from timm.models.layers import to_2tuple, trunc_normal_
from timm.models.layers import DropPath, to_2tuple

class Cross(nn.Module):
    def __init__(self, n_channels=3, n_classes=1):
        '''
        n_channels : number of channels of the input.
                        By default 3, because we have RGB images
        n_labels : number of channels of the ouput.
                      By default 3 (2 labels + 1 for the background)
        '''
        super().__init__()
        self.encoder = timm.create_model('hrnet_w18_small_v2', pretrained=True, features_only=True)

        self.classifier = nn.Sequential(
            nn.Dropout(p=0.4, inplace=True),
            nn.Linear(in_features=1024, out_features=512, bias=True),
            nn.Dropout(p=0.4, inplace=True),
            nn.Linear(in_features=512, out_features=256, bias=True),
            nn.Dropout(p=0.4, inplace=True),
            nn.Linear(in_features=256, out_features=40, bias=True),
        )

    def forward(self, x):

        x = x.float()
        b, c, h, w = x.shape

        x1, x2, x3, x4, x5 = self.encoder(x)

        x = F.adaptive_avg_pool2d(x5, 1)
        x = self.classifier(x)
        return x






