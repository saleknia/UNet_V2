import utils
from utils import cosine_scheduler
import torch
import torch.nn as nn
import torch.optim as optim
from torch.nn.modules.loss import CrossEntropyLoss
from utils import DiceLoss,atten_loss,prototype_loss,IM_loss,M_loss,CriterionPixelWise
from tqdm import tqdm
from utils import print_progress
import torch.nn.functional as F
import warnings
from utils import calc_loss, FocalLoss
warnings.filterwarnings("ignore")

def one_hot_loss(exist_pred, targets):
    targets=targets.cpu()
    exist_pred=exist_pred.cpu()
    yp = torch.zeros(6,9)
    for i in range(6):
        unique_num = torch.unique(targets[i])
        for j in range(9):
            if j in unique_num:
                yp[i,j] = 1.0
            else:
                yp[i,j] = 0.0
    loss = torch.nn.functional.binary_cross_entropy(input=exist_pred, target=yp)
    return loss

def loss_kd_regularization(outputs, masks):
    """
    loss function for mannually-designed regularization: Tf-KD_{reg}
    """
    correct_prob = 0.95    # the probability for correct class in u(k)
    K = outputs.size(1)

    teacher_scores = torch.ones_like(outputs).cuda()
    teacher_scores = teacher_scores*(1-correct_prob)/(K-1)  # p^d(k)

    teacher_scores[masks] = correct_prob

    return teacher_scores

def prediction_map_distillation(y, masks) :
    """
    basic KD loss function based on "Distilling the Knowledge in a Neural Network"
    https://arxiv.org/abs/1503.02531
    :param y: student score map
    :param teacher_scores: teacher score map
    :param T:  for softmax
    :return: loss value
    """
    y = y.cuda()
    masks = masks.long()
    masks = masks.cuda()

    masks_temp = F.one_hot(masks, num_classes=9)
    masks_temp = torch.permute(masks_temp, (0, 3, 1, 2))
    masks_temp = masks_temp.bool()

    teacher_scores = loss_kd_regularization(outputs=y, masks=masks_temp)

    return teacher_scores

# def prediction_map_distillation(y, masks, T=4.0) :
#     """
#     basic KD loss function based on "Distilling the Knowledge in a Neural Network"
#     https://arxiv.org/abs/1503.02531
#     :param y: student score map
#     :param teacher_scores: teacher score map
#     :param T:  for softmax
#     :return: loss value
#     """
#     y = y.cuda()
#     masks = masks.long()
#     masks = masks.cuda()

#     bin_masks = masks
#     bin_masks[bin_masks!=0] = 1.0 

#     masks_temp = F.one_hot(masks, num_classes=9)
#     masks_temp = torch.permute(masks_temp, (0, 3, 1, 2))
#     masks_temp = masks_temp.bool()

#     teacher_scores = loss_kd_regularization(outputs=y, masks=masks_temp)

#     # y_prime = y * bin_masks.unsqueeze(dim=1).expand_as(y)
#     # teacher_scores_prime = teacher_scores * bin_masks.unsqueeze(dim=1).expand_as(teacher_scores)

#     y_prime = y
#     teacher_scores_prime = teacher_scores 

#     p = F.log_softmax(y_prime / T , dim=1)
#     q = F.softmax(teacher_scores_prime / T, dim=1)

#     p = p.view(-1, 2)
#     q = q.view(-1, 2)

#     l_kl = F.kl_div(p, q, reduction='batchmean') * (T ** 2)
#     return l_kl


def trainer(end_epoch,epoch_num,model,dataloader,optimizer,device,ckpt,num_class,lr_scheduler,writer,logger,loss_function):
    torch.autograd.set_detect_anomaly(True)
    print(f'Epoch: {epoch_num} ---> Train , lr: {optimizer.param_groups[0]["lr"]}')

    model=model.to(device)
    model.train()

    loss_total = utils.AverageMeter()
    loss_dice_total = utils.AverageMeter()
    loss_ce_total = utils.AverageMeter()
    loss_proto_total = utils.AverageMeter()
    loss_kd_total = utils.AverageMeter()

    Eval = utils.Evaluator(num_class=num_class)

    mIOU = 0.0
    Dice = 0.0

    accuracy = utils.AverageMeter()

    ce_loss = CrossEntropyLoss()
    dice_loss = DiceLoss(num_class)
    ##################################################################
    # kd_out_loss = IM_loss()
    # kd_out_loss = CriterionPixelWise()
    kd_loss = M_loss()    
    proto_loss = loss_function
    ##################################################################
    ##################################################################
    # kd_loss = loss_function
    ##################################################################
    total_batchs = len(dataloader)
    loader = dataloader 

    base_iter = (epoch_num-1) * total_batchs
    iter_num = base_iter
    max_iterations = end_epoch * total_batchs
    # max_iterations = 50 * total_batchs

    for batch_idx, (inputs, targets) in enumerate(loader):

        inputs, targets = inputs.to(device), targets.to(device)

        targets = targets.float()

        # outputs = model(inputs)
        # outputs, up3, up2, up1  = model(inputs)
        # outputs, e5 = model(inputs)
        # outputs, probs1, probs2, probs3, probs4, up4, up3, up2, up1 = model(inputs)
        # outputs, up4, up3, up2, up1, up0 = model(inputs)
        # outputs, up4, up3, up2, up1 = model(inputs)
        
        outputs, up4, up3, up2, up1 = model(inputs)
        # e5, e4, e3, e2 = model(inputs, pretrain=True)
        # outputs = torch.zeros(inputs.shape,device='cuda')
     
        targets = targets.long()
        predictions = torch.argmax(input=outputs,dim=1).long()
        overlap = (predictions==targets).float()
        t_masks = targets * overlap
        targets = targets.float()

        loss_ce = ce_loss(outputs, targets[:].long())
        loss_dice = dice_loss(outputs, targets, softmax=True)

        # loss_proto = proto_loss(masks=targets.clone(), t_masks=t_masks, up4=up4, up3=up3, up2=up2, up1=up1)
        # loss_kd = kd_loss(e5=e5, e4=e4, e3=e3, e2=e2)

        loss_proto = 0.0
        loss_kd = 0.0
        # loss_ce = 0
        # loss_dice = 0

        # loss_kd_out = prediction_map_distillation(y=outputs, masks=targets)
        # loss_kd_out = kd_out_loss(masks=targets.clone(), x4=up4, x3=up3, x2=up2, x1=up1)
        # loss_kd = kd_loss(e5)
        ###############################################
        alpha = 0.01
        beta = 0.01
        loss = 0.5 * loss_ce + 0.5 * loss_dice 
        # loss = 0.5 * loss_ce + 0.5 * loss_dice + alpha * loss_proto 
        # loss = 0.5 * loss_ce + 0.5 * loss_dice + beta * loss_kd
        # loss = loss_kd 
        ###############################################

        lr_ = 0.1 * (1.0 - iter_num / max_iterations) ** 0.9

        for param_group in optimizer.param_groups:
            param_group['lr'] = lr_

        iter_num = iter_num + 1        
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        lr_scheduler.step()


        loss_total.update(loss)
        loss_dice_total.update(loss_dice)
        loss_ce_total.update(loss_ce)
        loss_proto_total.update(loss_proto)
        loss_kd_total.update(loss_kd)
        ###############################################
        targets = targets.long()

        predictions = torch.argmax(input=outputs,dim=1).long()
        Eval.add_batch(gt_image=targets,pre_image=predictions)

        accuracy.update(Eval.Pixel_Accuracy())

        print_progress(
            iteration=batch_idx+1,
            total=total_batchs,
            prefix=f'Train {epoch_num} Batch {batch_idx+1}/{total_batchs} ',
            # suffix=f'Dice_loss = {loss_dice_total.avg:.4f} , CE_loss={loss_ce_total.avg:.4f} , Att_loss = {loss_att_total.avg:.6f} , mIoU = {Eval.Mean_Intersection_over_Union()*100:.2f} , Dice = {Eval.Dice()*100:.2f}',
            # suffix=f'Dice_loss = {loss_dice_total.avg:.4f} , CE_loss={loss_ce_total.avg:.4f} , mIoU = {Eval.Mean_Intersection_over_Union()*100:.2f} , Dice = {Eval.Dice()*100:.2f}',          
            # suffix=f'Dice_loss = {0.5*loss_dice_total.avg:.4f} , CE_loss = {0.5*loss_ce_total.avg:.4f} , proto_loss = {alpha*loss_proto_total.avg:.8f} , Dice = {Eval.Dice()*100:.2f}',         
            suffix=f'Dice_loss = {0.5*loss_dice_total.avg:.4f} , CE_loss = {0.5*loss_ce_total.avg:.4f} , proto_loss = {alpha*loss_proto_total.avg:.8f} , kd_loss = {beta*loss_kd_total.avg:.4f}, Dice = {Eval.Dice()*100:.2f}',          
            # suffix=f'Dice_loss = {0.5*loss_dice_total.avg:.4f} , CE_loss = {0.5*loss_ce_total.avg:.4f} , loss_kd = {beta*loss_kd_total.avg:.8f} , Dice = {Eval.Dice()*100:.2f}',          
            bar_length=45
        )  
  
    # acc = 100*accuracy.avg
    # mIOU = 100*Eval.Mean_Intersection_over_Union()
    # Dice = 100*Eval.Dice()
    acc = 100*accuracy.avg
    mIOU = 100*Eval.Mean_Intersection_over_Union()
    Dice,Dice_per_class = Eval.Dice(per_class=True)
    Dice,Dice_per_class = 100*Dice,100*Dice_per_class

    if writer is not None:
        writer.add_scalar('Loss/train', loss_total.avg.item(), epoch_num)
        writer.add_scalar('Acc/train', acc.item(), epoch_num)
        writer.add_scalar('Dice/train', Dice.item(), epoch_num)
        writer.add_scalar('MIoU/train', mIOU.item(), epoch_num)

    if lr_scheduler is not None:
        lr_scheduler.step()        
        
    logger.info(f'Epoch: {epoch_num} ---> Train , Loss: {loss_total.avg:.4f} , mIoU: {mIOU:.2f} , Dice: {Dice:.2f} , Pixel Accuracy: {acc:.2f}, lr: {optimizer.param_groups[0]["lr"]}')

    # Save checkpoint
    if ckpt is not None:
        ckpt.save_best(acc=Dice, acc_per_class=Dice_per_class, epoch=epoch_num, net=model, optimizer=optimizer,lr_scheduler=lr_scheduler)
    if ckpt is not None:
        ckpt.save_last(acc=Dice, acc_per_class=Dice_per_class, epoch=epoch_num, net=model, optimizer=optimizer,lr_scheduler=lr_scheduler)
    # if ckpt is not None and (epoch_num==end_epoch):
    #     ckpt.save_last(acc=Dice, acc_per_class=Dice_per_class, epoch=epoch_num, net=model, optimizer=optimizer,lr_scheduler=lr_scheduler)
    # if ckpt is not None and (early_stopping < ckpt.early_stopping(epoch_num)):
    #     ckpt.save_last(acc=Dice, acc_per_class=Dice_per_class, epoch=epoch_num, net=model, optimizer=optimizer,lr_scheduler=lr_scheduler)  


