import utils
import torch
from utils import print_progress
from torch.nn.modules.loss import CrossEntropyLoss
from utils import DiceLoss, hd95
import warnings
from medpy import metric
import medpy
import numpy as np
import pickle
from utils import proto
warnings.filterwarnings("ignore")
import ttach as tta
from torchnet.meter import mAPMeter

def label_smoothing(labels):
    """
    loss function for label smoothing regularization
    """
    alpha = 0.1
    N = 40  # batch_size
    C = 40  # number of classes
    smoothed_labels = torch.full(size=(N, C), fill_value= alpha / (C - 1)).cuda()
    smoothed_labels.scatter_(dim=1, index=torch.unsqueeze(labels, dim=1), value=1-alpha)

    return smoothed_labels


transforms = tta.Compose(
    [
        tta.HorizontalFlip(),
        tta.Rotate90(angles=[0, 180]),      
    ]
)

def tester(end_epoch,epoch_num,model,dataloader,device,ckpt,num_class,writer,logger,optimizer,lr_scheduler,early_stopping):
    model.eval()

    # model = tta.ClassificationTTAWrapper(model, tta.aliases.five_crop_transform(crop_height=200, crop_width=200), merge_mode='mean')
    # model = tta.ClassificationTTAWrapper(model, transforms, merge_mode='mean')


    loss_total = utils.AverageMeter()
    accuracy   = utils.AverageMeter()
    # accuracy = mAPMeter()

    ce_loss = CrossEntropyLoss()
    total_batchs = len(dataloader)
    loader = dataloader

    with torch.no_grad():
        for batch_idx, (inputs, targets) in enumerate(loader):

            res = 0.0

            inputs, targets = inputs.to(device), targets.to(device)

            targets = targets.float()

            outputs = model(inputs)
            # prob = torch.softmax(outputs, dim=1)

            # print(outputs)

            loss_ce = ce_loss(outputs, targets[:].long())
            loss = loss_ce
            loss_total.update(loss)

            targets = targets.long()

            predictions = torch.argmax(input=outputs,dim=1).long()

            accuracy.update(torch.sum(targets==predictions)/torch.sum(targets==targets))
            # accuracy.add(torch.softmax(outputs.clone().detach(), dim=1), torch.nn.functional.one_hot(targets.long(), num_classes=40))

            # if 0.0 < torch.sum(targets==0.0):          
            #     accuracy.update(torch.sum((targets+predictions)==0.0)/torch.sum(targets==0.0))

            # if 0.0 < torch.sum(targets):
            #     accuracy.update(torch.sum((targets+predictions)==2.0)/torch.sum(targets))

            print_progress(
                iteration=batch_idx+1,
                total=total_batchs,
                prefix=f'Test {epoch_num} Batch {batch_idx+1}/{total_batchs} ',
                suffix=f'loss= {loss_total.avg:.4f} , Accuracy= {accuracy.avg*100:.2f} ',
                # suffix=f'loss= {loss_total.avg:.4f} , Accuracy= {accuracy.value().item()*100:.2f} ',
                bar_length=45
            )  

        acc = 100*accuracy.avg
        # acc = 100*accuracy.value().item()


        logger.info(f'Epoch: {epoch_num} ---> Test , Loss: {loss_total.avg:.4f} , Accuracy: {acc:.2f}') 



