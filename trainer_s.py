import utils
from utils import cosine_scheduler
import torch
import numpy as np
import torch.nn as nn
import torch.optim as optim
from torch.nn.modules.loss import CrossEntropyLoss
from tqdm import tqdm
from utils import print_progress
import torch.nn.functional as F
import warnings
from utils import focal_loss, Dilation2d, Erosion2d
from torch.autograd import Variable
from torch.nn.functional import mse_loss as MSE
from utils import importance_maps_distillation as imd
from valid_s import valid_s
from sklearn.metrics import confusion_matrix
from SCL import SemanticConnectivityLoss
warnings.filterwarnings("ignore")

erosion = Erosion2d(1, 1, 9, soft_max=False)
dilate = Dilation2d(1, 1, 9, soft_max=False)

class DiceLoss(nn.Module):
    def __init__(self, weight=None, size_average=True):
        super(DiceLoss, self).__init__()

    def forward(self, inputs, targets, smooth=1e-5):
        
        #comment out if your model contains a sigmoid or equivalent activation layer
        inputs = F.sigmoid(inputs)       
        
        #flatten label and prediction tensors
        inputs = inputs.view(-1)
        targets = targets.view(-1)
        
        intersection = (inputs * targets).sum()                            
        dice = (2.*intersection + smooth)/(inputs.sum() + targets.sum() + smooth)  
        
        return 1 - dice

def structure_loss(pred, mask):
    weit = 1 + 5*torch.abs(F.avg_pool2d(mask, kernel_size=31, stride=1, padding=15) - mask)
    wbce = F.binary_cross_entropy_with_logits(pred, mask, reduction='none')
    wbce = (weit*wbce).sum(dim=(2, 3)) / weit.sum(dim=(2, 3))

    pred = torch.sigmoid(pred)
    inter = ((pred * mask)*weit).sum(dim=(2, 3))
    union = ((pred + mask)*weit).sum(dim=(2, 3))
    wiou = 1 - (inter + 1)/(union - inter+1)
    return (wbce + wiou).mean()

def at(x, exp):
    """
    attention value of a feature map
    :param x: feature
    :return: attention value
    """
    return F.normalize(x.pow(exp).mean(1).view(x.size(0), -1))


def importance_maps_distillation(s, t, exp=2):
    """
    importance_maps_distillation KD loss, based on "Paying More Attention to Attention:
    Improving the Performance of Convolutional Neural Networks via Attention Transfer"
    https://arxiv.org/abs/1612.03928
    :param exp: exponent
    :param s: student feature maps
    :param t: teacher feature maps
    :return: imd loss value
    """
    if s.shape[2] != t.shape[2]:
        t = F.interpolate(t, s.size()[-2:], mode='bilinear')
    return torch.sum((at(s, exp) - at(t, exp)).pow(2), dim=1).mean()

def attention_loss(up4, up3, up2, up1):
    loss = 0.0
    loss = loss + importance_maps_distillation(s=up3, t=up4.detach().clone())
    loss = loss + importance_maps_distillation(s=up2, t=up3.detach().clone())
    loss = loss + importance_maps_distillation(s=up1, t=up2.detach().clone())
    return loss

class CriterionPixelWise(nn.Module):
    def __init__(self):
        super(CriterionPixelWise, self).__init__()

    def forward(self, preds_S, preds_T):
        preds_T.detach()
        assert preds_S.shape == preds_T.shape,'the output dim of teacher and student differ'
        N,C,W,H = preds_S.shape
        softmax_pred_T = preds_T.permute(0,2,3,1).contiguous().view(-1,C)
        logsoftmax = nn.LogSoftmax(dim=1)
        loss = (torch.sum( - softmax_pred_T * logsoftmax(preds_S.permute(0,2,3,1).contiguous().view(-1,C))))/W/H
        return loss


class Evaluator(object):
    ''' For using this evaluator target and prediction
        dims should be [B,H,W] '''
    def __init__(self):
        self.reset()
        
    def Pixel_Accuracy(self):
        Acc = torch.tensor(np.mean(self.acc))
        return Acc

    def Mean_Intersection_over_Union(self,per_class=False,show=False):
        IoU = torch.tensor(np.mean(self.iou))
        return IoU

    def Dice(self,per_class=False,show=False):
        Dice = torch.tensor(np.mean(self.dice))
        return Dice

    def add_batch(self, gt_image, pre_image):
        gt_image=gt_image.int().detach().cpu().numpy()
        pre_image=pre_image.int().detach().cpu().numpy()
        for i in range(gt_image.shape[0]):
            tn, fp, fn, tp = confusion_matrix(gt_image[i].reshape(-1), pre_image[i].reshape(-1)).ravel()
            Acc = (tp + tn) / (tp + tn + fp + fn)
            IoU = (tp) / (tp + fp + fn)
            Dice =  (2 * tp) / ((2 * tp) + fp + fn)
            self.acc.append(Acc)
            self.iou.append(IoU)
            self.dice.append(Dice)

    def reset(self):
        self.acc = []
        self.iou = []
        self.dice = []

def trainer_s(end_epoch,epoch_num,model,dataloader,optimizer,device,ckpt,num_class,lr_scheduler,writer,logger,loss_function):
    torch.autograd.set_detect_anomaly(True)
    print(f'Epoch: {epoch_num} ---> Train , lr: {optimizer.param_groups[0]["lr"]}')
    
    model=model.to('cuda')
    model.train()

    loss_total = utils.AverageMeter()
    loss_ce_total = utils.AverageMeter()
    loss_dice_total = utils.AverageMeter()

    Eval = Evaluator()

    mIOU = 0.0
    Dice = 0.0

    total_batchs = len(dataloader['train'])
    loader = dataloader['train'] 
    pos_weight = dataloader['pos_weight']
    dice_loss = DiceLoss()
    ce_loss = torch.nn.BCEWithLogitsLoss(pos_weight=None)
    scl_loss = SemanticConnectivityLoss()
    # ce_loss = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    base_iter = (epoch_num-1) * total_batchs
    iter_num = base_iter
    max_iterations = end_epoch * total_batchs
    scaler = torch.cuda.amp.GradScaler()
    alpha = 1.0
    for batch_idx, (inputs, targets) in enumerate(loader):

        inputs, targets = inputs.to(device), targets.to(device)
        targets = targets.float()
        # boundary = (dilate(targets.unsqueeze(dim=1).cpu()) - erosion(targets.unsqueeze(dim=1).cpu())).squeeze(dim=1).cuda()
        # boundary = (targets.unsqueeze(dim=1).cpu() - erosion(targets.unsqueeze(dim=1).cpu())).squeeze(dim=1).cuda()

        inputs = inputs.float()
        with torch.autocast(device_type=device, dtype=torch.float16):
            outputs = model(inputs)
            if type(outputs)==tuple:
                loss_ce = ce_loss(outputs[0], targets.unsqueeze(dim=1)) + (alpha * (ce_loss(outputs[1], boundary.unsqueeze(dim=1)) + F.mse_loss(outputs[1], boundary)))
                loss_dice = dice_loss(inputs=outputs[0], targets=targets) + (alpha * dice_loss(inputs=outputs[1], targets=boundary))
                loss = loss_ce + loss_dice 
            else:
                loss_ce = ce_loss(outputs, targets.unsqueeze(dim=1)) + 0.01 * F.mse_loss(outputs, targets)
                loss_dice = dice_loss(inputs=outputs, targets=targets)
                loss = loss_ce + loss_dice 



        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad()

    # for batch_idx, (inputs, targets) in enumerate(loader):

    #     inputs, targets = inputs.to(device), targets.to(device)
    #     targets = targets.float()
    #     inputs = inputs.float()
    #     outputs = model(inputs)
    #     if type(outputs)==tuple:
    #         loss_ce = ce_loss(outputs[0], targets.unsqueeze(dim=1)) + ce_loss(outputs[1], targets.unsqueeze(dim=1)) + ce_loss(outputs[2], targets.unsqueeze(dim=1)) 
    #         loss_dice = dice_loss(inputs=outputs[0], targets=targets) + dice_loss(inputs=outputs[1], targets=targets) + dice_loss(inputs=outputs[2], targets=targets)
    #         loss = loss_ce + loss_dice         
    #     else:
    #         loss_ce = ce_loss(outputs, targets.unsqueeze(dim=1)) 
    #         loss_dice = dice_loss(inputs=outputs, targets=targets)
    #         loss = loss_ce + loss_dice

    #     # lr_ = 0.01 * (1.0 - iter_num / max_iterations) ** 0.9

    #     # for param_group in optimizer.param_groups:
    #     #     param_group['lr'] = lr_

    #     # iter_num = iter_num + 1   

    #     # iter_num = iter_num + 1 
    #     # if iter_num % (total_batchs*3)==0:
    #     #     for param_group in optimizer.param_groups:
    #     #         param_group['lr'] = param_group['lr'] * 0.5   

    #     optimizer.zero_grad()
    #     loss.backward()
    #     optimizer.step()

        # optimizer.zero_grad()
        # loss.backward()
        # optimizer.step()

        loss_total.update(loss)
        loss_ce_total.update(loss_ce)
        loss_dice_total.update(loss_dice)

        targets = targets.long()

        if type(outputs)==tuple:
            predictions = torch.round((torch.sigmoid(torch.squeeze(outputs[0], dim=1))))

        else:
            predictions = torch.round(torch.sigmoid(torch.squeeze(outputs, dim=1)))

        # predictions = torch.round(torch.squeeze(outputs, dim=1))
        # predictions = torch.round(torch.sigmoid(torch.squeeze(outputs, dim=1)))
        Eval.add_batch(gt_image=targets,pre_image=predictions)
        # accuracy.update(Eval.Pixel_Accuracy())

        print_progress(
            iteration=batch_idx+1,
            total=total_batchs,
            prefix=f'Train {epoch_num} Batch {batch_idx+1}/{total_batchs} ',
            # suffix=f'loss = {loss_total.avg:.4f} , loss_ce = {loss_ce_total.avg:.4f} , loss_dice = {loss_dice_total.avg:.4f} , loss_scl = {loss_scl_total.avg:.4f} , Dice = {Eval.Dice()*100.0:.2f} , IoU = {Eval.Mean_Intersection_over_Union()*100.0:.2f} , Pixel Accuracy = {Eval.Pixel_Accuracy()*100.0:.2f}',          
            suffix=f'loss = {loss_total.avg:.4f} , Dice = {Eval.Dice()*100.0:.2f} , IoU = {Eval.Mean_Intersection_over_Union()*100.0:.2f} , Pixel Accuracy = {Eval.Pixel_Accuracy()*100.0:.2f}',          

            bar_length=45
        )  
  
    acc =  Eval.Pixel_Accuracy() * 100.0
    mIOU = Eval.Mean_Intersection_over_Union() * 100.0

    Dice = Eval.Dice() * 100.
    Dice_per_class = Dice * 100.0

    if lr_scheduler is not None:
        lr_scheduler.step()        
        
    logger.info(f'Epoch: {epoch_num} ---> Train , Loss = {loss_total.avg:.4f} , Dice = {Dice:.2f} , IoU = {mIOU:.2f} , Pixel Accuracy = {acc:.2f} , lr = {optimizer.param_groups[0]["lr"]}')

    valid_s(end_epoch,epoch_num,model,dataloader,device,ckpt,num_class,writer,logger,optimizer)



