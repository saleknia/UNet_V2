from re import S, X
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from torchvision.models import resnet50, efficientnet_b0, EfficientNet_B0_Weights, efficientnet_b1, EfficientNet_B1_Weights, efficientnet_b2, EfficientNet_B2_Weights, EfficientNet_B3_Weights, efficientnet_b3, EfficientNet_B5_Weights, efficientnet_b4, EfficientNet_B4_Weights, efficientnet_b5, efficientnet_v2_s, EfficientNet_V2_S_Weights
from torchvision.models.segmentation import DeepLabV3_ResNet50_Weights, DeepLabV3_MobileNet_V3_Large_Weights
from torchvision.models import efficientnet_v2_m, EfficientNet_V2_M_Weights
from torchvision.models import efficientnet_v2_l, EfficientNet_V2_L_Weights
import random
from torchvision.models import resnet50, efficientnet_b4, EfficientNet_B4_Weights
from torch.nn import init
from .Mobile_netV2_loss import Mobile_netV2_loss

from timm.layers import LayerNorm2d

import torch
from torch.autograd import Variable as V
import torchvision.models as models
from torchvision import transforms as trn
from torch.nn import functional as F
import os
from PIL import Image
import timm
from .wideresnet import *
from .wideresnet import recursion_change_bn

from pyts.image import GramianAngularField as GAF
from pyts.preprocessing import MinMaxScaler as scaler
from pyts.image import MarkovTransitionField as MTF
from mit_semseg.models import ModelBuilder
from pyts.image import RecurrencePlot

from torchvision import transforms
transform_test = transforms.Compose([
    transforms.Resize((384, 384)),
])
from torchvision.transforms import FiveCrop, Lambda
from efficientvit.seg_model_zoo import create_seg_model

from efficientvit.cls_model_zoo import create_cls_model
from timm.layers import LayerNorm2d

from transformers import CLIPProcessor, CLIPModel
from PIL import Image
class Mobile_netV2(nn.Module):
    def __init__(self, num_classes=67, pretrained=True):
        super(Mobile_netV2, self).__init__()

        
        # self.model     = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        # self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        # self.class_txt = class_txt

        # model = resnet18(num_classes=365)
        # checkpoint = torch.load('/content/wideresnet18_places365.pth.tar', map_location='cpu')
        # state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}
        # model.load_state_dict(state_dict)

        # self.model = model
        # self.model.fc = nn.Sequential(
        #     nn.Dropout(p=0.5, inplace=True),
        #     nn.Linear(in_features=512, out_features=num_classes, bias=True),
        # )
        
        ############################################################
        ############################################################

        # model = torchvision.models.convnext_small(weights='DEFAULT')

        # self.model = model 

        # self.model.classifier[2] = nn.Sequential(
        #     nn.Dropout(p=0.5, inplace=True),
        #     nn.Linear(in_features=768, out_features=num_classes, bias=True))

        # # self.model.classifier[0] = nn.Identity()
        
        # for param in self.model.parameters():
        #     param.requires_grad = False

        # for param in self.model.features[6].parameters():
        #     param.requires_grad = True

        # for param in self.model.features[7].parameters():
        #     param.requires_grad = True

        # for param in self.model.classifier.parameters():
        #     param.requires_grad = True

        # # self.teacher = convnext_teacher()
        # # self.teacher = convnext_small()

        ############################################################
        ############################################################

        # model = efficientnet_b2(weights=EfficientNet_B2_Weights)

        # model.features[0][0].stride = (1, 1)

        # self.model = model
        # # self.avgpool = model.avgpool

        # for param in self.model.features[0:5].parameters():
        #     param.requires_grad = False

        # self.model.classifier[0].p            = 0.5
        # self.model.classifier[1].out_features = 67

        ############################################################
        ############################################################

        # scene      = models.__dict__['resnet50'](num_classes=365)
        # checkpoint = torch.load('/content/resnet50_places365.pth.tar', map_location='cpu')
        # state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}

        # scene.load_state_dict(state_dict)

        # self.scene = scene

        # for param in self.scene.parameters():
        #     param.requires_grad = False

        # self.scene.fc = nn.Sequential(
        #     nn.Dropout(p=0.5, inplace=True),
        #     nn.Linear(in_features=2048, out_features=256, bias=True),
        # )

        # model = timm.create_model('timm/convnextv2_tiny.fcmae_ft_in1k', pretrained=True)

        # self.model = model 

        # for param in self.model.parameters():
        #     param.requires_grad = False

        # self.model.head.fc = nn.Sequential(
        #     nn.Dropout(p=0.5, inplace=True),
        #     nn.Linear(in_features=768, out_features=256, bias=True),
        # )

        # seg = create_seg_model(name="b2", dataset="ade20k", weight_url="/content/drive/MyDrive/b2.pt")

        # seg.input_stem.op_list[0].conv.stride  = (1, 1)
        # seg.input_stem.op_list[0].conv.padding = (0, 0)

        # # seg.head.output_ops[0].op_list[0] = nn.Identity()

        # self.seg = seg

        # for param in self.seg.parameters():
        #     param.requires_grad = False

        # for param in self.seg.head.parameters():
        #     param.requires_grad = True

        # for param in self.seg.backbone.stages[-1].parameters():
        #     param.requires_grad = True

        # self.avgpool = nn.AvgPool2d()
        # self.dropout = nn.Dropout(0.5)
        # self.fc_SEM  = nn.Sequential(nn.Linear(in_features=2400, out_features=num_classes, bias=True))

        #################################################################################
        #################################################################################

        # # model      = models.__dict__['resnet50'](num_classes=365)
        # # checkpoint = torch.load('/content/resnet50_places365.pth.tar', map_location='cpu')
        # # state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}

        # model      = models.__dict__['resnet50'](num_classes=365)
        # checkpoint = torch.load('/content/resnet50_places365.pth.tar', map_location='cpu')
        # state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}

        # model.load_state_dict(state_dict)

        # self.model = model

        # for param in self.model.parameters():
        #     param.requires_grad = False

        # for param in self.model.layer4.parameters():
        #     param.requires_grad = True

        # self.model.fc = nn.Sequential(
        #     nn.Dropout(p=0.5, inplace=True),
        #     nn.Linear(in_features=2048, out_features=num_classes, bias=True),
        # )

        # #################################################################################
        # #################################################################################


        # model      = models.__dict__['densenet161'](num_classes=365)
        # checkpoint = torch.load('/content/densenet161_places365.pth.tar', map_location='cpu')
        # state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}
        # state_dict = {str.replace(k,'.1','1'): v for k,v in state_dict.items()}
        # state_dict = {str.replace(k,'.2','2'): v for k,v in state_dict.items()}

        # model.load_state_dict(state_dict)

        # self.model = model

        # for param in self.model.parameters():
        #     param.requires_grad = False

        # # for param in self.model.features.denseblock4.parameters():
        # #     param.requires_grad = True

        # for i, module in enumerate(model.features.denseblock4):
        #     if 14 < i:
        #         for param in model.features.denseblock4[module].parameters():
        #             param.requires_grad = True


        # self.model.classifier = nn.Sequential(
        #     nn.Dropout(p=0.5, inplace=True),
        #     nn.Linear(in_features=2208, out_features=67, bias=True),
        # )

        # #################################################################################
        # #################################################################################

        # model = timm.create_model('mvitv2_tiny', pretrained=True, features_only=True)
        # head  = timm.create_model('mvitv2_tiny', pretrained=True).head

        # self.model = model

        # for param in self.model.parameters():
        #     param.requires_grad = False

        # for param in self.model.model.stages[2:].parameters():
        #     param.requires_grad = True

        # self.avgpool = nn.AvgPool2d(7, stride=1)

        # self.head = nn.Sequential(
        #     nn.Dropout(p=0.5, inplace=True),
        #     nn.Linear(in_features=768, out_features=num_classes, bias=True))

        #################################################################################
        #################################################################################

        # model = create_seg_model(name="b2", dataset="ade20k", weight_url="/content/drive/MyDrive/b2.pt").backbone

        # model.input_stem.op_list[0].conv.stride  = (1, 1)
        # model.input_stem.op_list[0].conv.padding = (0, 0)

        # self.model = model

        # for param in self.model.parameters():
        #     param.requires_grad = False

        # for param in self.model.stages[-1].parameters():
        #     param.requires_grad = True

        # for param in self.model.stages[-2].parameters():
        #     param.requires_grad = True

        # self.dropout = nn.Dropout(0.5)
        # self.avgpool = nn.AvgPool2d(14, stride=1)
        # self.fc_SEM  = nn.Linear(384, num_classes)

        #################################################################################
        #################################################################################

        # model = create_cls_model(name="b2", weight_url="/content/drive/MyDrive/b2-r256.pt")

        # self.model = model

        # print(model)

        # for param in self.model.parameters():
        #     param.requires_grad = False

        # for param in self.model.stages[-1].parameters():
        #     param.requires_grad = True

        # for param in self.model.head.parameters():
        #     param.requires_grad = True
      
        # self.dropout = nn.Dropout(0.5)
        # self.avgpool = nn.AvgPool2d(8, stride=1)
        # self.fc_SEM  = nn.Linear(384, num_classes)

        #################################################################################
        #################################################################################

        # model = timm.create_model('convnext_tiny.fb_in1k', pretrained=True)
        # model = timm.create_model('tf_efficientnet_b0.in1k', pretrained=True)

        # self.model = model 

        # self.model.classifier = nn.Sequential(nn.Dropout(p=0.5, inplace=True), nn.Linear(in_features=1280, out_features=num_classes, bias=True))

        # for param in self.model.parameters():
        #     param.requires_grad = False

        # for param in self.model.blocks[4:].parameters():
        #     param.requires_grad = True

        # for param in self.model.classifier.parameters():
        #     param.requires_grad = True

        #################################################################################
        #################################################################################

        model = timm.create_model('convnext_tiny.fb_in1k', pretrained=True)

        self.model = model 

        for param in self.model.parameters():
            param.requires_grad = False

        self.model.head.fc = nn.Sequential(
            nn.Dropout(p=0.5, inplace=True),
            nn.Linear(in_features=768, out_features=num_classes, bias=True),
        )

        for param in self.model.stages[-1].parameters():
            param.requires_grad = True

        for param in self.model.head.parameters():
            param.requires_grad = True

        #################################################################################
        #################################################################################

        # model = timm.create_model('timm/maxvit_tiny_tf_224.in1k', pretrained=True)

        # self.model = model 

        # for param in self.model.parameters():
        #     param.requires_grad = False

        # self.model.head.fc = nn.Sequential(
        #     nn.Dropout(p=0.5, inplace=False),
        #     nn.Linear(in_features=512, out_features=num_classes, bias=True),
        # )

        # for param in self.model.stages[-1].parameters():
        #     param.requires_grad = True

        # for param in self.model.stages[-2].parameters():
        #     param.requires_grad = True

        # for param in self.model.head.parameters():
        #     param.requires_grad = True

        ##################################################################################
        ##################################################################################

        # self.model = timm.create_model('convnext_tiny.fb_in1k', pretrained=True, features_only=True)
        
        # self.head  = timm.create_model('convnext_tiny.fb_in1k', pretrained=True).head 
        
        # self.head.fc = nn.Sequential(
        #             nn.Dropout(p=0.5, inplace=True),
        #             nn.Linear(in_features=768, out_features=num_classes, bias=True),
        #         )

        # for param in self.model.parameters():
        #     param.requires_grad = False

        # for param in self.model.stages_2.parameters():
        #     param.requires_grad = True

        # for param in self.model.stages_3.parameters():
        #     param.requires_grad = True

        # for param in self.head.parameters():
        #     param.requires_grad = True

        ##################################################################################
        ##################################################################################

        # self.features = timm.create_model('timm/efficientvit_l1.r224_in1k', pretrained=True, features_only=True)
        # self.head     = timm.create_model('timm/efficientvit_l1.r224_in1k', pretrained=True).head

        # for param in self.features.parameters():
        #     param.requires_grad = False

        # # for param in self.features.stages_3.blocks[-3:].parameters():
        # #     param.requires_grad = True

        # self.head.classifier[4] = nn.Sequential(
        #     nn.Dropout(p=0.5, inplace=True),
        #     nn.Linear(in_features=3200, out_features=num_classes, bias=True),
        # )

        # for param in self.head.parameters():
        #     param.requires_grad = True

        #################################################################################
        #################################################################################

        # classifier = timm.create_classifier('tf_efficientnet_b0', pretrained=True)

        # self.classifier = classifier 

        # for param in self.classifier.blocks[0:5].parameters():
        #     param.requires_grad = False

        # for param in self.classifier.conv_stem.parameters():
        #     param.requires_grad = False

        # self.classifier.classifier = nn.Sequential(
        #     nn.Dropout(p=0.5, inplace=True),
        #     nn.Linear(in_features=1280, out_features=num_classes, bias=True),
        # )

        # for param in self.model.blocks[5][10:15].parameters():
        #     param.requires_grad = True

        # self.avgpool = torch.nn.AvgPool2d(kernel_size=4, stride=4, padding=0)

        # self.model = B0()

        # self.transform_0 = transforms.Compose([transforms.Resize((224, 224))])

        # self.transform = transforms.Compose([
        #     transforms.Resize((384, 384)),
        # ])

        # self.count = 0.0
        # self.batch = 0.0

        # self.transform = torchvision.transforms.Compose([FiveCrop(224), Lambda(lambda crops: torch.stack([crop for crop in crops]))])

        # loaded_data_teacher = torch.load('/content/drive/MyDrive/checkpoint/tiny.pth', map_location='cpu')
        # pretrained_teacher  = loaded_data_teacher['net']
        # a = pretrained_teacher.copy()
        # for key in a.keys():
        #     if 'teacher' in key:
        #         pretrained_teacher.pop(key)
        # self.load_state_dict(pretrained_teacher)

        #################################
        #################################
        # self.inspector = None
        # self.inspector = femto()
        #################################
        #################################
        # self.b0 = maxvit()
        # self.b1 = mvit_tiny()
        # self.b2 = convnext_tiny()

        # loaded_data_teacher = torch.load('/content/drive/MyDrive/checkpoint/normal.pth', map_location='cpu')
        # pretrained_teacher  = loaded_data_teacher['net']
        # a = pretrained_teacher.copy()
        # for key in a.keys():
        #     if 'teacher' in key:
        #         pretrained_teacher.pop(key)
        # self.load_state_dict(pretrained_teacher)

        # self.model = teacher_ensemble()

        # self.count = 0.0
        # self.batch = 0.0
        # self.transform = torchvision.transforms.Compose([FiveCrop(224), Lambda(lambda crops: torch.stack([crop for crop in crops]))])
        #################################
        #################################

        # self.features  = timm.create_model('timm/convnext_pico.d1_in1k', pretrained=True, features_only=True) #, out_indices=[2])
        # self.head      = timm.create_model('timm/convnext_pico.d1_in1k', pretrained=True).head
        # self.head.norm = LayerNorm2d((3840,))
        # self.head.fc   = nn.Sequential(nn.Dropout(p=0.5, inplace=True) , nn.Linear(in_features=512, out_features=num_classes, bias=True))

        # self.expert_g = expert_g()
        # self.expert_s = expert_s()
        # self.expert_p = expert_p()
        # self.expert_l = expert_l()
        # self.expert_h = expert_h()
        # self.expert_w = expert_w()

        # for param in self.features.parameters():
        #     param.requires_grad = False

        # for param in self.features.stages_3.parameters():
        #     param.requires_grad = True

        # for param in self.features.stages_2.parameters():
        #     param.requires_grad = True

        # self.teacher = teacher()

    def forward(self, x_in):

        # b, c, w, h = x_in.shape

        # print(x_in.device)

        # image   = Image.open(x_in[0])
        # inputs  = self.processor(text=self.class_txt, images=image, return_tensors="pt", padding=True)
        # inputs = inputs.to('cuda')
        # outputs = self.model(**inputs)
        # logits_per_image = outputs.logits_per_image  # this is the image-text similarity score
        # probs = logits_per_image.softmax(dim=1)

        # x = self.model(x_in)
        # x = x['stage_final']
        # x = self.avgpool(x)
        # x = x.view(x.size(0), -1)
        # x = self.dropout(x)
        # x = self.fc_SEM(x)

        x = self.model(x_in)

        # x3 = self.avgpool(x3)
        # x3 = x3.view(x3.size(0), -1)

        # x = self.head(x3)

        # x = self.avgpool(x)
        # x = x.view(x.size(0), -1)
        # x = self.dropout(x)
        # x = self.fc_SEM(x)

        # x0, x1, x2, x3 = self.features(x_in)
        # x = self.head(x3)

        # x_in = self.features(x_in)[0]

        # g, index = self.expert_g(x_in)

        # w = self.expert_w(x_in)
        # s = self.expert_s(x_in)
        # p = self.expert_p(x_in)
        # l = self.expert_l(x_in)
        # h = self.expert_h(x_in)

        # hi = index[:, 0]
        # li = index[:, 1]
        # pi = index[:, 2]
        # si = index[:, 3]
        # wi = index[:, 4]

        # wi = wi.unsqueeze(dim=1).unsqueeze(dim=2).unsqueeze(dim=3).expand_as(w)
        # si = si.unsqueeze(dim=1).unsqueeze(dim=2).unsqueeze(dim=3).expand_as(s)
        # pi = pi.unsqueeze(dim=1).unsqueeze(dim=2).unsqueeze(dim=3).expand_as(p)
        # li = li.unsqueeze(dim=1).unsqueeze(dim=2).unsqueeze(dim=3).expand_as(l)
        # hi = hi.unsqueeze(dim=1).unsqueeze(dim=2).unsqueeze(dim=3).expand_as(h)

        # w = w * wi
        # s = s * si
        # p = p * pi
        # l = l * li
        # h = h * hi

        # x3 = torch.cat([w, s, p, l, h], dim=1)

        # x3 = w + s + p + l + h + g

        # x  = self.head(x3)

        # features_t = self.teacher(x_in)
        # features_s = [x2, x3]

        # if (not self.training):

        #     self.batch = self.batch + 1.0

        #     if self.batch == 1335:
        #         print(self.count)

        #     x0, x1 = x_in[0], x_in[1]
            
        #     x = self.model(x0)
        #     # x = self.head(x[4])
        #     x = torch.softmax(x, dim=1)

        #     if (x.max() < 0.5):

        #         y = self.transform(x1)
        #         ncrops, bs, c, h, w = y.size()
        #         x = self.model(y.view(-1, c, h, w))
        #         # x = self.head(x[4])
        #         # x = torch.softmax(x, dim=1).mean(0, keepdim=True)
        #         # x = x.mean(0, keepdim=True)

        #         x = torch.softmax(x, dim=1)
        #         a, b, c = torch.topk(x.max(dim=1).values, 3).indices
        #         x = ((x[a] + x[b] + x[c]) / 3.0).unsqueeze(dim=0)

        #         self.count = self.count + 1.0
        
        # else:
        #     b, c, w, h = x_in.shape
        #     x = self.model(x_in)



        if self.training:
            return x
        else:
            return torch.softmax(x, dim=1)

labels = {
            'airport inside': 0,
            'art studio': 1,
            'auditorium': 2,
            'bakery': 3,
            'bar': 4,
            'bathroom': 5,
            'bedroom': 6,
            'bookstore': 7,
            'bowling': 8,
            'buffet': 9,
            'casino': 10,
            'children room': 11,
            'church': 12,
            'classroom': 13,
            'cloister': 14,
            'closet': 15,
            'clothing store': 16,
            'computer room': 17,
            'concert hall': 18,
            'corridor': 19,
            'deli': 20,
            'dental office': 21,
            'dining room': 22,
            'elevator': 23,
            'fastfood restaurant': 24,
            'florist': 25,
            'game room': 26,
            'garage': 27,
            'green house': 28,
            'grocery store': 29,
            'gym': 30,
            'hair salon': 31,
            'hospital room': 32,
            'bus inside': 33,
            'subway inside': 34,
            'jewellery shop': 35,
            'kindergarden': 36,
            'kitchen': 37,
            'wet lab': 38,
            'laundromat': 39,
            'library': 40,
            'livingroom': 41,
            'lobby': 42,
            'locker room': 43,
            'mall': 44,
            'meeting room': 45,
            'movie theater': 46,
            'museum': 47,
            'nursery': 48,
            'office': 49,
            'operating room': 50,
            'pantry': 51,
            'pool inside': 52,
            'prison cell': 53,
            'restaurant': 54,
            'restaurant kitchen': 55,
            'shoe shop': 56,
            'staircase': 57,
            'studio music': 58,
            'subway': 59,
            'toy store': 60,
            'train station': 61,
            'tv studio': 62,
            'video store': 63,
            'waiting room': 64,
            'warehouse': 65,
            'wine cellar': 66
 }

class_txt = [f'a photo of a {x}.' for x in labels]

class expert_g(nn.Module):
    def __init__(self, num_classes=5, pretrained=True):
        super(expert_g, self).__init__()

        self.features = timm.create_model('convnext_tiny.fb_in1k', pretrained=True, features_only=True)
        self.head     = timm.create_model('convnext_tiny.fb_in1k', pretrained=True).head
        self.head.fc  = nn.Sequential(nn.Dropout(p=0.5, inplace=True), nn.Linear(in_features=768, out_features=num_classes, bias=True))

        for param in self.parameters():
            param.requires_grad = False

        loaded_data_teacher = torch.load('/content/drive/MyDrive/checkpoint/expert_g.pth', map_location='cpu')
        pretrained_teacher  = loaded_data_teacher['net']
        a = pretrained_teacher.copy()
        for key in a.keys():
            if 'teacher' in key:
                pretrained_teacher.pop(key)
        self.load_state_dict(pretrained_teacher)

    def forward(self, x_in):

        # x0, x1, x2, x3 = self.features(x_in)
        x3 = self.features.stages_3(x_in)
        x  = self.head(x3)
        x  = x.softmax(dim=1)

        # x = torch.nn.functional.one_hot(x.max(dim=1)[1], num_classes=5)

        MH1 = torch.nn.functional.one_hot(x.max(dim=1)[1], num_classes=5)
        x   = x * ((MH1-1.0)*(-1.0))
        MH2 = torch.nn.functional.one_hot(x.max(dim=1)[1], num_classes=5)
        x   = x * ((MH2-1.0)*(-1.0)) 

        return x3, MH1 + MH2

class expert_w(nn.Module):
    def __init__(self, num_classes=15, pretrained=True):
        super(expert_w, self).__init__()

        self.features = timm.create_model('convnext_tiny.fb_in1k', pretrained=True, features_only=True)
        self.head     = timm.create_model('convnext_tiny.fb_in1k', pretrained=True).head
        self.head.fc  = nn.Sequential(nn.Dropout(p=0.5, inplace=True), nn.Linear(in_features=768, out_features=num_classes, bias=True))

        for param in self.parameters():
            param.requires_grad = False

        loaded_data_teacher = torch.load('/content/drive/MyDrive/checkpoint/expert_w.pth', map_location='cpu')
        pretrained_teacher  = loaded_data_teacher['net']
        a = pretrained_teacher.copy()
        for key in a.keys():
            if 'teacher' in key:
                pretrained_teacher.pop(key)
        self.load_state_dict(pretrained_teacher)

    def forward(self, x_in):

        x3 = self.features.stages_3(x_in)

        # x0, x1, x2, x3 = self.features(x_in)

        # x  = self.head(x3)

        return x3

class expert_s(nn.Module):
    def __init__(self, num_classes=12, pretrained=True):
        super(expert_s, self).__init__()

        self.features = timm.create_model('convnext_tiny.fb_in1k', pretrained=True, features_only=True)
        self.head     = timm.create_model('convnext_tiny.fb_in1k', pretrained=True).head
        self.head.fc  = nn.Sequential(nn.Dropout(p=0.5, inplace=True), nn.Linear(in_features=768, out_features=num_classes, bias=True))

        for param in self.parameters():
            param.requires_grad = False

        loaded_data_teacher = torch.load('/content/drive/MyDrive/checkpoint/expert_s.pth', map_location='cpu')
        pretrained_teacher  = loaded_data_teacher['net']
        a = pretrained_teacher.copy()
        for key in a.keys():
            if 'teacher' in key:
                pretrained_teacher.pop(key)
        self.load_state_dict(pretrained_teacher)

    def forward(self, x_in):

        x3 = self.features.stages_3(x_in)

        # x0, x1, x2, x3 = self.features(x_in)
        # x              = self.head(x3)

        # x  = x.softmax(dim=1).max(dim=1)[0]
        # x  = x.unsqueeze(dim=1)

        return x3

class expert_p(nn.Module):
    def __init__(self, num_classes=14, pretrained=True):
        super(expert_p, self).__init__()

        self.features = timm.create_model('convnext_tiny.fb_in1k', pretrained=True, features_only=True)
        self.head     = timm.create_model('convnext_tiny.fb_in1k', pretrained=True).head
        self.head.fc  = nn.Sequential(nn.Dropout(p=0.5, inplace=True), nn.Linear(in_features=768, out_features=num_classes, bias=True))

        for param in self.parameters():
            param.requires_grad = False

        loaded_data_teacher = torch.load('/content/drive/MyDrive/checkpoint/expert_p.pth', map_location='cpu')
        pretrained_teacher  = loaded_data_teacher['net']
        a = pretrained_teacher.copy()
        for key in a.keys():
            if 'teacher' in key:
                pretrained_teacher.pop(key)
        self.load_state_dict(pretrained_teacher)

    def forward(self, x_in):

        x3 = self.features.stages_3(x_in)

        # x0, x1, x2, x3 = self.features(x_in)
        # x              = self.head(x3)

        # x  = x.softmax(dim=1).max(dim=1)[0]
        # x  = x.unsqueeze(dim=1)

        return x3

class expert_l(nn.Module):
    def __init__(self, num_classes=12, pretrained=True):
        super(expert_l, self).__init__()

        self.features = timm.create_model('convnext_tiny.fb_in1k', pretrained=True, features_only=True)
        self.head     = timm.create_model('convnext_tiny.fb_in1k', pretrained=True).head
        self.head.fc  = nn.Sequential(nn.Dropout(p=0.5, inplace=True), nn.Linear(in_features=768, out_features=num_classes, bias=True))

        for param in self.parameters():
            param.requires_grad = False

        loaded_data_teacher = torch.load('/content/drive/MyDrive/checkpoint/expert_l.pth', map_location='cpu')
        pretrained_teacher  = loaded_data_teacher['net']
        a = pretrained_teacher.copy()
        for key in a.keys():
            if 'teacher' in key:
                pretrained_teacher.pop(key)
        self.load_state_dict(pretrained_teacher)

    def forward(self, x_in):

        x3 = self.features.stages_3(x_in)

        # x0, x1, x2, x3 = self.features(x_in)
        # x = self.head(x3)

        # x  = x.softmax(dim=1).max(dim=1)[0]
        # x  = x.unsqueeze(dim=1)

        return x3

class expert_h(nn.Module):
    def __init__(self, num_classes=14, pretrained=True):
        super(expert_h, self).__init__()

        self.features = timm.create_model('convnext_tiny.fb_in1k', pretrained=True, features_only=True)
        self.head     = timm.create_model('convnext_tiny.fb_in1k', pretrained=True).head
        self.head.fc  = nn.Sequential(nn.Dropout(p=0.5, inplace=True), nn.Linear(in_features=768, out_features=num_classes, bias=True))

        for param in self.parameters():
            param.requires_grad = False

        loaded_data_teacher = torch.load('/content/drive/MyDrive/checkpoint/expert_h.pth', map_location='cpu')
        pretrained_teacher  = loaded_data_teacher['net']
        a = pretrained_teacher.copy()
        for key in a.keys():
            if 'teacher' in key:
                pretrained_teacher.pop(key)
        self.load_state_dict(pretrained_teacher)

    def forward(self, x_in):

        x3 = self.features.stages_3(x_in)

        # x0, x1, x2, x3 = self.features(x_in)
        # x = self.head(x3)

        # x  = x.softmax(dim=1).max(dim=1)[0]
        # x  = x.unsqueeze(dim=1)

        return x3

alpha = 0.0

class teacher_ensemble(nn.Module):
    def __init__(self, num_classes=67, pretrained=True):
        super(teacher_ensemble, self).__init__()

        self.maxvit = maxvit_model()
        self.scene  = scene()
        self.seg    = seg()

    def forward(self, x0):

        # b, c, w, h = x0.shape

        a = self.maxvit(x0)
        b = self.scene(x0)
        c = self.seg(x0) 

        x = (a + b + c) / 3.0

        return x

class scene(nn.Module):
    def __init__(self, num_classes=67, pretrained=True):
        super(scene, self).__init__()
       
        model      = models.__dict__['resnet50'](num_classes=365)
        checkpoint = torch.load('/content/resnet50_places365.pth.tar', map_location='cpu')
        state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}

        model.load_state_dict(state_dict)

        self.model = model

        for param in self.model.parameters():
            param.requires_grad = False

        for param in self.model.layer4[-1].parameters():
            param.requires_grad = True

        self.model.fc = nn.Sequential(
            nn.Dropout(p=0.5, inplace=True),
            nn.Linear(in_features=2048, out_features=67, bias=True),
        )
        loaded_data_teacher = torch.load('/content/drive/MyDrive/checkpoint/scene.pth', map_location='cpu')
        pretrained_teacher  = loaded_data_teacher['net']
        a = pretrained_teacher.copy()
        for key in a.keys():
            if 'teacher' in key:
                pretrained_teacher.pop(key)
        self.load_state_dict(pretrained_teacher)

        self.transform = torchvision.transforms.Compose([FiveCrop(224), Lambda(lambda crops: torch.stack([crop for crop in crops]))])

    def forward(self, x_in):
        # b, c, w, h = x0.shape

        # x = self.model(x0)

        if (not self.training):

            x0, x1 = x_in[0], x_in[1]
            
            x = self.model(x0)
            x = torch.softmax(x, dim=1)

            if (x.max() < alpha):

                y = self.transform(x1)
                ncrops, bs, c, h, w = y.size()
                x = self.model(y.view(-1, c, h, w))

                x = torch.softmax(x.mean(0, keepdim=True), dim=1)
                # x = torch.softmax(x, dim=1).mean(0, keepdim=True)

                # x = torch.softmax(x, dim=1)
                # a, b, c = torch.topk(x.max(dim=1).values, 3).indices
                # x = ((x[a] + x[b] + x[c]) / 3.0).unsqueeze(dim=0)
        
        else:
            b, c, w, h = x_in.shape
            x = self.model(x_in)

        return x # torch.softmax(x, dim=1)


class seg(nn.Module):
    def __init__(self, num_classes=67, pretrained=True):
        super(seg, self).__init__()
       
        model = create_seg_model(name="b2", dataset="ade20k", weight_url="/content/drive/MyDrive/b2.pt").backbone

        model.input_stem.op_list[0].conv.stride  = (1, 1)
        model.input_stem.op_list[0].conv.padding = (0, 0)

        self.model = model

        for param in self.model.parameters():
            param.requires_grad = False

        for param in self.model.stages[-1].parameters():
            param.requires_grad = True

        self.dropout = nn.Dropout(0.5)
        self.avgpool = nn.AvgPool2d(14, stride=1)
        self.fc_SEM  = nn.Linear(384, num_classes)

        loaded_data_teacher = torch.load('/content/drive/MyDrive/checkpoint/seg.pth', map_location='cpu')
        pretrained_teacher  = loaded_data_teacher['net']
        a = pretrained_teacher.copy()
        for key in a.keys():
            if 'teacher' in key:
                pretrained_teacher.pop(key)
        self.load_state_dict(pretrained_teacher)

        self.transform = torchvision.transforms.Compose([FiveCrop(224), Lambda(lambda crops: torch.stack([crop for crop in crops]))])

    def forward(self, x_in):
        # b, c, w, h = x0.shape

        # x = self.model(x0)
        # x = x['stage_final']
        # x = self.avgpool(x)
        # x = x.view(x.size(0), -1)
        # x = self.dropout(x)
        # x = self.fc_SEM(x)

        if (not self.training):

            x0, x1 = x_in[0], x_in[1]
                
            x = self.model(x0)
            x = x['stage_final']
            x = self.avgpool(x)
            x = x.view(x.size(0), -1)
            x = self.dropout(x)
            x = self.fc_SEM(x)
            x = torch.softmax(x, dim=1)

            if (x.max() < alpha):

                y = self.transform(x1)
                ncrops, bs, c, h, w = y.size()

                x = self.model(y.view(-1, c, h, w))
                x = x['stage_final']
                x = self.avgpool(x)
                x = x.view(x.size(0), -1)
                x = self.dropout(x)
                x = self.fc_SEM(x)

                x = torch.softmax(x.mean(0, keepdim=True), dim=1)
                # x = torch.softmax(x, dim=1).mean(0, keepdim=True)

                # x = torch.softmax(x, dim=1)
                # a, b, c = torch.topk(x.max(dim=1).values, 3).indices
                # x = ((x[a] + x[b] + x[c]) / 3.0).unsqueeze(dim=0)
        
        else:
            b, c, w, h = x_in.shape
            x = self.model(x_in)

        return x # torch.softmax(x, dim=1)

class maxvit_model(nn.Module):
    def __init__(self, num_classes=67, pretrained=True):
        super(maxvit_model, self).__init__()

        model = timm.create_model('timm/maxvit_tiny_tf_224.in1k', pretrained=True)

        self.model = model 

        for param in self.model.parameters():
            param.requires_grad = False

        self.model.head.fc = nn.Sequential(
            nn.Dropout(p=0.5, inplace=False),
            nn.Linear(in_features=512, out_features=num_classes, bias=True),
        )

        for param in self.model.stages[-1].parameters():
            param.requires_grad = True

        for param in self.model.head.parameters():
            param.requires_grad = True

        loaded_data_teacher = torch.load('/content/drive/MyDrive/checkpoint/max.pth', map_location='cpu')
        pretrained_teacher  = loaded_data_teacher['net']
        a = pretrained_teacher.copy()
        for key in a.keys():
            if 'teacher' in key:
                pretrained_teacher.pop(key)
        self.load_state_dict(pretrained_teacher)

        self.transform = torchvision.transforms.Compose([FiveCrop(224), Lambda(lambda crops: torch.stack([crop for crop in crops]))])
        
    def forward(self, x_in):
        # b, c, w, h = x0.shape

        if (not self.training):

            x0, x1 = x_in[0], x_in[1]
            
            x = self.model(x0)
            x = torch.softmax(x, dim=1)

            if (x.max() < alpha):

                y = self.transform(x1)
                ncrops, bs, c, h, w = y.size()
                x = self.model(y.view(-1, c, h, w))
                
                x = torch.softmax(x.mean(0, keepdim=True), dim=1)
                # x = torch.softmax(x, dim=1).mean(0, keepdim=True)

                # x = torch.softmax(x, dim=1)
                # a, b, c = torch.topk(x.max(dim=1).values, 3).indices
                # x = ((x[a] + x[b] + x[c]) / 3.0).unsqueeze(dim=0)
        
        else:
            b, c, w, h = x_in.shape
            x = self.model(x_in)

        return x # torch.softmax(x, dim=1)
