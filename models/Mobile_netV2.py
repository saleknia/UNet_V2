import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from torchvision.models import resnet18, resnet50, efficientnet_b0, EfficientNet_B0_Weights, efficientnet_b1, EfficientNet_B1_Weights, efficientnet_b2, EfficientNet_B2_Weights, EfficientNet_B3_Weights, efficientnet_b3, EfficientNet_B5_Weights, efficientnet_b4, EfficientNet_B4_Weights, efficientnet_b5, efficientnet_v2_s, EfficientNet_V2_S_Weights
from torchvision.models.segmentation import DeepLabV3_ResNet50_Weights, DeepLabV3_MobileNet_V3_Large_Weights
from torchvision.models import efficientnet_v2_m, EfficientNet_V2_M_Weights
from torchvision.models import efficientnet_v2_l, EfficientNet_V2_L_Weights
import random
from torch.nn import init
from .Mobile_netV2_loss import Mobile_netV2_loss

import torch
from torch.autograd import Variable as V
import torchvision.models as models
from torchvision import transforms as trn
from torch.nn import functional as F
import os
from PIL import Image

class Mobile_netV2(nn.Module):
    def __init__(self, num_classes=40, pretrained=True):
        super(Mobile_netV2, self).__init__()

        # self.teacher = Mobile_netV2_teacher()
        # loaded_data_teacher = torch.load('/content/drive/MyDrive/checkpoint_B0_78_62/Mobile_NetV2_MIT-67_best.pth', map_location='cuda')
        # pretrained_teacher = loaded_data_teacher['net']
        # a = pretrained_teacher.copy()
        # for key in a.keys():
        #     if 'teacher' in key:
        #         pretrained_teacher.pop(key)
        # self.teacher.load_state_dict(pretrained_teacher)

        # for param in self.teacher.parameters():
        #     param.requires_grad = False

        # model = efficientnet_v2_s(weights=EfficientNet_V2_S_Weights)

        # model = torchvision.models.regnet_y_400mf(weights='DEFAULT')

        model = efficientnet_b0(weights=EfficientNet_B0_Weights)

        # teacher = models.__dict__['resnet18'](num_classes=365)
        # checkpoint = torch.load('/content/resnet18_places365.pth.tar', map_location='cpu')
        # state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}
        # teacher.load_state_dict(state_dict)

        # self.teacher = teacher

        # for param in self.teacher.parameters():
        #     param.requires_grad = False

        # for param in self.teacher.layer4[-1].parameters():
        #     param.requires_grad = True

        # self.teacher.fc = nn.Sequential(nn.Dropout(p=0.5, inplace=True), nn.Linear(in_features=512, out_features=num_classes, bias=True))
        # self.teacher.conv1.stride = (1, 1)

        # model = torchvision.models.convnext_tiny(weights='DEFAULT')

        model.features[0][0].stride = (1, 1)

        self.features = model.features

        for param in self.features[0:4].parameters():
            param.requires_grad = False

        self.avgpool = self.teacher.avgpool

        self.classifier = nn.Sequential(
            nn.Dropout(p=0.5, inplace=True),
            nn.Linear(in_features=1280, out_features=num_classes, bias=True))

        # self.classifier = nn.Sequential(
        #     nn.Dropout(p=0.5, inplace=True),
        #     nn.Linear(in_features=1280, out_features=512, bias=True),
        #     nn.Dropout(p=0.5, inplace=True),
        #     nn.Linear(in_features=512, out_features=256, bias=True),
        #     nn.Dropout(p=0.5, inplace=True),
        #     nn.Linear(in_features=256, out_features=num_classes, bias=True),
        # )


    def forward(self, x0):
        b, c, w, h = x0.shape

        # x = self.teacher.conv1(x0)
        # x = self.teacher.bn1(x)
        # x = self.teacher.relu(x)
        # x = self.teacher.maxpool(x)
        # x = self.teacher.layer1(x)

        # x1_t = self.teacher.layer2(x)
        # x2_t = self.teacher.layer3(x1_t)
        # x3_t = self.teacher.layer4(x2_t)

        x1 = self.features[0:4](x0)
        x2 = self.features[4:6](x1)
        x3 = self.features[6:9](x2)

        # x = self.teacher(x0)

        # x3 = self.features(x0)

        x = self.avgpool(x3)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)

        return x

        # if self.training:
        #     return x, x1, x2, x3, x1_t, x2_t, x3_t
        # else:
        #     return x


# class Mobile_netV2(nn.Module):
#     def __init__(self, num_classes=40, pretrained=True):
#         super(Mobile_netV2, self).__init__()

#         # self.teacher = Mobile_netV2_teacher()
#         # loaded_data_teacher = torch.load('/content/drive/MyDrive/checkpoint_VL_96_97/Mobile_NetV2_Standford40_best.pth', map_location='cuda')
#         # pretrained_teacher = loaded_data_teacher['net']
#         # a = pretrained_teacher.copy()
#         # for key in a.keys():
#         #     if 'teacher' in key:
#         #         pretrained_teacher.pop(key)
#         # self.teacher.load_state_dict(pretrained_teacher)

#         # for param in self.teacher.parameters():
#         #     param.requires_grad = False

#         # self.teacher = Mobile_netV2_loss()
#         # self.teacher.eval()
#         # for param in self.teacher.parameters():
#         #     param.requires_grad = False

#         # model = efficientnet_b2(weights=EfficientNet_B2_Weights)

#         # model = efficientnet_v2_s(weights=EfficientNet_V2_S_Weights)

#         # model = efficientnet_v2_m(weights=EfficientNet_V2_M_Weights)

#         # model = efficientnet_v2_l(weights=EfficientNet_V2_L_Weights)

#         model = torchvision.models.convnext_tiny(weights='DEFAULT')
#         model.features[0][0].stride = (2, 2)
        
#         # model.features[0][0].stride = (1, 1)

#         self.features = model.features

#         for param in self.features[0:6].parameters():
#             param.requires_grad = False

#         # for param in self.features[0:4].parameters():
#         #     param.requires_grad = False

#         self.avgpool = model.avgpool

#         # self.classifier = nn.Sequential(
#         #     nn.Dropout(p=0.4, inplace=True),
#         #     nn.Linear(in_features=1280, out_features=512, bias=True),
#         #     nn.Dropout(p=0.4, inplace=True),
#         #     nn.Linear(in_features=512, out_features=256, bias=True),
#         #     nn.Dropout(p=0.4, inplace=True),
#         #     nn.Linear(in_features=256, out_features=40, bias=True),
#         # )

#         self.classifier = nn.Sequential(
#             nn.Dropout(p=0.5, inplace=True),
#             nn.Linear(in_features=1280, out_features=40, bias=True))
        
#     def forward(self, x0):
#         b, c, w, h = x0.shape

#         # x_t, x1_t, x2_t = self.teacher(x0)

#         x_t, x1_t, x2_t, x3_t = self.teacher(x0)

#         # print(x_t)

#         # x1 = self.features[0:7](x0)
#         # x2 = self.features[7:8](x1)
#         # x3 = self.features[8:9](x2)

#         x1 = self.features[0:4](x0)
#         x2 = self.features[4:6](x1)
#         x3 = self.features[6:9](x2)

#         # x0 = self.features[0:6](x0)
#         # x1 = self.features[6:7](x0)
#         # x2 = self.features[7:8](x1)
#         # x3 = self.features[8:9](x2)

#         # x3 = self.features(x0)

#         x = self.avgpool(x3)
#         x = x.view(x.size(0), -1)
#         x = self.classifier(x)

#         # print(x1.shape)
#         # print(x2.shape)
#         # print(x3.shape)

#         # print(x1_t.shape)
#         # print(x2_t.shape)
#         # print(x3_t.shape)

#         if self.training:
#             return x, x_t, x1, x2, x3, x1_t, x2_t, x3_t
#         else:
#             return x

#         # return x

#         # if self.training:
#         #     return x#, x_t#, x1, x2, x_t, x1_t, x2_t
#         # else:
#         #     return self.avgpool(x3) # torch.softmax(x, dim=1)

class Mobile_netV2_teacher(nn.Module):
    def __init__(self, num_classes=40, pretrained=True):
        super(Mobile_netV2_teacher, self).__init__()

        # model = efficientnet_b0(weights=EfficientNet_B0_Weights)
        # # model.features[0][0].stride = (1, 1)

        # self.features = model.features
        # self.avgpool = model.avgpool

        # for param in self.features[0:9].parameters():
        #     param.requires_grad = False

        # self.classifier = nn.Sequential(
        #     nn.Dropout(p=0.5, inplace=True),
        #     nn.Linear(in_features=1280, out_features=67, bias=True))

        # self.classifier = nn.Sequential(
        #     nn.Dropout(p=0.4, inplace=True),
        #     nn.Linear(in_features=1536, out_features=512, bias=True),
        #     nn.Dropout(p=0.4, inplace=True),
        #     nn.Linear(in_features=512, out_features=256, bias=True),
        #     nn.Dropout(p=0.4, inplace=True),
        #     nn.Linear(in_features=256, out_features=40, bias=True),
        # )

        teacher = models.__dict__['resnet18'](num_classes=365)
        checkpoint = torch.load('/content/resnet18_places365.pth.tar', map_location='cpu')
        state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}
        teacher.load_state_dict(state_dict)

        self.teacher = teacher

        for param in self.teacher.parameters():
            param.requires_grad = False

        for param in self.teacher.layer4[-1].parameters():
            param.requires_grad = True

        self.teacher.fc = nn.Sequential(nn.Dropout(p=0.5, inplace=True), nn.Linear(in_features=512, out_features=num_classes, bias=True))
        self.teacher.conv1.stride = (1, 1)

        self.avgpool = self.teacher.avgpool

    def forward(self, x0):
        b, c, w, h = x0.shape

        # x = self.features(x0)

        # x1 = self.features[0:4](x0)
        # x2 = self.features[4:6](x1)
        # x3 = self.features[6:9](x2)

        # # x0 = self.features[0:6](x0)
        # # x1 = self.features[6:7](x0)
        # # x2 = self.features[7:8](x1)
        # # x3 = self.features[8:9](x2)

        # x = self.avgpool(x3) 
        
        # x = x.view(x.size(0), -1)

        # x = self.classifier(x)

        # # if self.training:
        # #     return x 
        # # else:
        # #     return torch.softmax(x, dim=1)

        # return torch.softmax(x, dim=1)#, x1, x2, x3


    # def forward(self, x0):
    #     b, c, w, h = x0.shape

    #     x1 = self.features[0:7](x0)
    #     x2 = self.features[7:8](x1)
    #     x3 = self.features[8:9](x2)

    #     x = self.avgpool(x3)
    #     x = x.view(x.size(0), -1)
    #     x = self.classifier(x)

    #     return x, x1, x2


# class Mobile_netV2(nn.Module):
#     def __init__(self, num_classes=40, pretrained=True):
#         super(Mobile_netV2, self).__init__()

#         self.teacher = Mobile_netV2_teacher()
#         loaded_data_teacher = torch.load('/content/drive/MyDrive/checkpoint_B3_86_80/Mobile_NetV2_Standford40_best.pth', map_location='cuda')
#         pretrained_teacher = loaded_data_teacher['net']
#         a = pretrained_teacher.copy()
#         for key in a.keys():
#             if 'teacher' in key:
#                 pretrained_teacher.pop(key)
#         self.teacher.load_state_dict(pretrained_teacher)

#         for param in self.teacher.parameters():
#             param.requires_grad = False

#         # model = efficientnet_v2_s(weights=EfficientNet_V2_S_Weights)

#         model = efficientnet_b0(weights=EfficientNet_B0_Weights)

#         # model.features[0][0].stride = (1, 1)

#         for param in model.features[0:5].parameters():
#             param.requires_grad = False

#         self.features = model.features
#         self.avgpool = model.avgpool

#         self.classifier = nn.Sequential(
#             nn.Dropout(p=0.5, inplace=True),
#             nn.Linear(in_features=1280, out_features=40, bias=True),
#         )

#         # self.classifier = nn.Sequential(
#         #     nn.Dropout(p=0.4, inplace=True),
#         #     nn.Linear(in_features=1280, out_features=512, bias=True),
#         #     nn.Dropout(p=0.4, inplace=True),
#         #     nn.Linear(in_features=512 , out_features=256, bias=True),
#         #     nn.Dropout(p=0.4, inplace=True),
#         #     nn.Linear(in_features=256 , out_features=40, bias=True),
#         # )

#     def forward(self, x0):
#         b, c, w, h = x0.shape

#         x1_t, x2_t = self.teacher(x0)

#         x1 = self.features[0:7](x0)
#         x2 = self.features[7:8](x1)
#         x3 = self.features[8:9](x2)

#         # x = self.features(x0)

#         x = self.avgpool(x3) 
#         x = x.view(x.size(0), -1)
#         x = self.classifier(x)

#         if self.training:
#             return x, x1, x2, x1_t, x2_t
#         else:
#             return torch.softmax(x, dim=1)










