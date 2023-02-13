import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import resnet18, resnet50, efficientnet_b0, EfficientNet_B0_Weights, efficientnet_b1, EfficientNet_B1_Weights, efficientnet_b4, EfficientNet_B4_Weights, EfficientNet_B6_Weights, efficientnet_b6
import torchvision
import random

# class Mobile_netV2(nn.Module):
#     def __init__(self, num_classes=40, pretrained=True):
#         super(Mobile_netV2, self).__init__()

#         model = resnet50(weights=torchvision.models.ResNet50_Weights.DEFAULT)
#         self.conv1 = model.conv1
#         self.bn1 = model.bn1
#         self.relu = model.relu
#         self.maxpool = model.maxpool
#         self.layer1 = model.layer1
#         self.layer2 = model.layer2
#         self.layer3 = model.layer3
#         self.layer4 = model.layer4
#         self.avgpool = model.avgpool
#         self.classifier = nn.Sequential(
#             nn.Dropout(p=0.4, inplace=True),
#             nn.Linear(in_features=2048, out_features=512, bias=True),
#             nn.Dropout(p=0.4, inplace=True),
#             nn.Linear(in_features=512, out_features=256, bias=True),
#             nn.Dropout(p=0.4, inplace=True),
#             nn.Linear(in_features=256, out_features=40, bias=True),
#         )
#         self.attention_1 = ParallelPolarizedSelfAttention(channel=256)
#         self.attention_2 = ParallelPolarizedSelfAttention(channel=512)
#         self.attention_3 = ParallelPolarizedSelfAttention(channel=1024)
#         # self.se = SEAttention(channel=1280)
#     def forward(self, x):
#         b, c, w, h = x.shape

#         x = self.conv1(x)
#         x = self.bn1(x)
#         x = self.relu(x)
#         x = self.maxpool(x)

#         x = self.layer1(x)
#         x = self.attention_1(x)
#         x = self.layer2(x)
#         x = self.attention_2(x)
#         x = self.layer3(x)
#         x = self.attention_3(x)
#         x = self.layer4(x)

#         x = self.avgpool(x)
#         x = x.view(x.size(0), -1)
#         x = self.classifier(x)
        
#         return x

class Mobile_netV2(nn.Module):
    def __init__(self, num_classes=40, pretrained=True):
        super(Mobile_netV2, self).__init__()

        model = efficientnet_b0(weights=EfficientNet_B0_Weights)
        # model.features[0][0].stride = (1, 1)
        self.features_1 = model.features[0:3]
        self.features_2 = model.features[3:4]
        self.features_3 = model.features[4:6]
        self.features_4 = model.features[6:]
        self.avgpool = model.avgpool
        self.classifier = nn.Sequential(
            nn.Dropout(p=0.4, inplace=True),
            nn.Linear(in_features=1280, out_features=512, bias=True),
            nn.Dropout(p=0.4, inplace=True),
            nn.Linear(in_features=512, out_features=256, bias=True),
            nn.Dropout(p=0.4, inplace=True),
            nn.Linear(in_features=256, out_features=40, bias=True),
        )
    def forward(self, x):
        b, c, w, h = x.shape

        x0 = self.features_1(x)
        x1 = self.features_2(x0)
        x2 = self.features_3(x1)
        x3 = self.features_4(x2)

        x3 = self.avgpool(x3)
        x3 = x3.view(x3.size(0), -1)
        x4 = self.classifier(x3)
        
        if self.training:
            return x4, x3
        else:
            return x4



