import os
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
import numpy as np
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support

from src.config import PROJECT_ROOT, DATASET_DIR, MODEL_SAVE_PATH, TRAIN_CONFIG
from src.data_loader import get_dataloaders
from src.model import OnionTransferNet

def train_transfer_learning():
    print("=" * 65)
    print("Starting 2-Stage Transfer Learning for Onion Quality Assessment")
    print("=" * 65)
    
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load dataset
    train_loader, valid_loader, test_loader, train_set, valid_set, test_set = get_dataloaders(
        dataset_dir=DATASET_DIR,
        batch_size=TRAIN_CONFIG.get("batch_size", 32),
        img_size=TRAIN_CONFIG.get("img_size", 224)
    )
    print(f"Dataset: Train={len(train_set)}, Valid={len(valid_set)}, Test={len(test_set)}")
    
    train_labels = [s["label"] for s in train_set.samples]
    bad_count = train_labels.count(0)
    good_count = train_labels.count(1)
    print(f"Class Distribution: Defective/Bad: {bad_count}, Healthy/Good: {good_count}")
    
    # Balanced class weighting
    total_samples = len(train_labels)
    weight_bad = total_samples / (2.0 * max(1, bad_count))
    weight_good = total_samples / (2.0 * max(1, good_count))
    class_weights = torch.tensor([weight_bad, weight_good], dtype=torch.float).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    
    # Initialize Pretrained Model
    backbone_choice = "mobilenet_v3_large" # Pretrained on ImageNet-1K V2
    model = OnionTransferNet(backbone_name=backbone_choice, num_classes=2, pretrained=True)
    model = model.to(device)
    
    # -------------------------------------------------------------
    # STAGE 1: Feature Extraction (Frozen Backbone, Warmup Head)
    # -------------------------------------------------------------
    print("\n--- STAGE 1: Feature Extraction (Training Top Head with Frozen Backbone) ---")
    model.freeze_backbone()
    optimizer_stage1 = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=1e-3,
        weight_decay=1e-4
    )
    
    for epoch in range(1, 3):
        model.train()
        running_loss = 0.0
        train_preds, train_targets = [], []
        
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer_stage1.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer_stage1.step()
            
            running_loss += loss.item() * images.size(0)
            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            train_preds.extend(preds)
            train_targets.extend(labels.cpu().numpy())
            
        train_acc = accuracy_score(train_targets, train_preds)
        print(f"[Stage 1 - Epoch {epoch}/2] Train Loss: {running_loss/len(train_set):.4f} | Train Acc: {train_acc*100:.2f}%")

    # -------------------------------------------------------------
    # STAGE 2: End-to-End Fine-Tuning with Differential Learning Rates
    # -------------------------------------------------------------
    print("\n--- STAGE 2: End-to-End Fine-Tuning (Unfrozen Backbone with Differential LR) ---")
    model.unfreeze_backbone()
    
    # Differential LR: Smaller LR for backbone features, higher for classifier head
    backbone_params = []
    head_params = []
    for name, param in model.named_parameters():
        if "classifier" in name or "fc" in name:
            head_params.append(param)
        else:
            backbone_params.append(param)
            
    optimizer_stage2 = optim.AdamW([
        {"params": backbone_params, "lr": 1e-4},
        {"params": head_params, "lr": 5e-4}
    ], weight_decay=1e-4)
    
    fine_tune_epochs = 4
    scheduler = CosineAnnealingLR(optimizer_stage2, T_max=fine_tune_epochs)
    
    best_val_f1 = 0.0
    start_time = time.time()
    
    for epoch in range(1, fine_tune_epochs + 1):
        model.train()
        running_loss = 0.0
        train_preds, train_targets = [], []
        
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer_stage2.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer_stage2.step()
            
            running_loss += loss.item() * images.size(0)
            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            train_preds.extend(preds)
            train_targets.extend(labels.cpu().numpy())
            
        scheduler.step()
        train_acc = accuracy_score(train_targets, train_preds)
        
        # Validation Evaluation
        model.eval()
        val_loss = 0.0
        val_preds, val_targets = [], []
        
        with torch.no_grad():
            for images, labels in valid_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * images.size(0)
                preds = torch.argmax(outputs, dim=1).cpu().numpy()
                val_preds.extend(preds)
                val_targets.extend(labels.cpu().numpy())
                
        val_loss /= len(valid_set)
        val_acc = accuracy_score(val_targets, val_preds)
        val_prec, val_rec, val_f1, _ = precision_recall_fscore_support(
            val_targets, val_preds, average='weighted', zero_division=0
        )
        
        print(f"[Stage 2 - Epoch {epoch}/{fine_tune_epochs}] "
              f"Train Loss: {running_loss/len(train_set):.4f} | Train Acc: {train_acc*100:.2f}% || "
              f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc*100:.2f}% | Val F1: {val_f1:.4f}")
        
        if val_f1 >= best_val_f1:
            best_val_f1 = val_f1
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            print(f" --> Saved best Transfer Learning checkpoint (Val F1: {val_f1:.4f})")
            
    print(f"\nTransfer Learning training completed. Best Validation F1: {best_val_f1:.4f}")
    
    # Evaluate Best Checkpoint on Test Set
    print("\n" + "=" * 65)
    print("Evaluating Best Transfer Learning Model on Test Set...")
    print("=" * 65)
    model.load_state_dict(torch.load(MODEL_SAVE_PATH))
    model.eval()
    
    test_preds, test_targets = [], []
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            test_preds.extend(preds)
            test_targets.extend(labels.numpy())
            
    print("\nTest Set Evaluation Report:")
    print(classification_report(test_targets, test_preds, labels=[0, 1], target_names=["BAD (Defect)", "GOOD (Healthy)"], zero_division=0))
    print("=" * 65)

if __name__ == "__main__":
    train_transfer_learning()
