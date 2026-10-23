import os
import csv
import cv2
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from typing import List, Dict, Any, Tuple
from src.config import DATASET_DIR, TRAIN_CONFIG

class OnionDataset(Dataset):
    """
    PyTorch Dataset for Onion Quality Classification.
    Parses images and _classes.csv annotations (BAD: 0, GOOD: 1).
    """
    def __init__(self, split_dir: str, transform=None):
        self.split_dir = split_dir
        self.transform = transform
        self.samples = [] # list of (img_path, label_idx, [bad_flag, good_flag])
        
        csv_path = os.path.join(split_dir, "_classes.csv")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Annotation file not found: {csv_path}")
            
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                fname = row['filename'].strip()
                img_path = os.path.join(split_dir, fname)
                if not os.path.exists(img_path):
                    continue
                    
                bad = int(row.get('BAD', 0))
                good = int(row.get('GOOD', 0))
                
                # Assign pure labels:
                # 0: Defective/Bad/Rotten/Sprouted, 1: Good/Healthy
                if good == 1 and bad == 0:
                    label = 1
                elif bad == 1 and good == 0:
                    label = 0
                else:
                    # Mixed image (contains both) - skip for single-label classifier training to avoid shortcut bias
                    continue
                
                self.samples.append({
                    "path": img_path,
                    "label": label,
                    "bad_flag": bad,
                    "good_flag": good
                })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        item = self.samples[idx]
        image = Image.open(item["path"]).convert("RGB")
        
        if self.transform:
            image = self.transform(image)
            
        label = torch.tensor(item["label"], dtype=torch.long)
        return image, label

def get_transforms(img_size: int = 224):
    """Returns train and validation/test torchvision transform pipelines."""
    train_transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=25),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    return train_transform, val_transform

def get_dataloaders(dataset_dir: str = DATASET_DIR, batch_size: int = 32, img_size: int = 224):
    """Creates train, valid, and test dataloaders."""
    train_tf, val_tf = get_transforms(img_size)
    
    train_set = OnionDataset(os.path.join(dataset_dir, "train"), transform=train_tf)
    valid_set = OnionDataset(os.path.join(dataset_dir, "valid"), transform=val_tf)
    test_set = OnionDataset(os.path.join(dataset_dir, "test"), transform=val_tf)
    
    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=0)
    valid_loader = DataLoader(valid_set, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=False, num_workers=0)
    
    return train_loader, valid_loader, test_loader, train_set, valid_set, test_set
