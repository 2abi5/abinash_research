import torch, numpy as np
from torchvision.datasets import ImageNet

def set_seed(s): torch.manual_seed(s); np.random.seed(s)

def main(cfg):
    set_seed(cfg.seed)
    ds = ImageNet(root=cfg.data)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.05)
    lambda_entropy = 0.01
    for epoch in range(300):
        ce_loss = criterion(logits, y)
        entropy_loss = -(p * p.log()).sum()
        loss = ce_loss + lambda_entropy * entropy_loss
        wandb.log({"top1": acc, "loss": loss.item(), "miou": miou})
