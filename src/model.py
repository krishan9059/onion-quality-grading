import torch
import torch.nn as nn
import torchvision.models as models

class OnionTransferNet(nn.Module):
    """
    Advanced Transfer Learning Neural Network for Onion Quality & Defect Classification.
    Supports state-of-the-art backbones (ResNet-50, MobileNetV3-Large, EfficientNet-B0)
    pre-trained on ImageNet-1K (V2 weights), with 2-stage transfer learning and fine-tuning support.
    """
    def __init__(self, backbone_name: str = "mobilenet_v3_large", num_classes: int = 2, pretrained: bool = True):
        super(OnionTransferNet, self).__init__()
        self.backbone_name = backbone_name
        
        if backbone_name == "resnet50":
            weights = models.ResNet50_Weights.DEFAULT if pretrained else None
            self.backbone = models.resnet50(weights=weights)
            in_features = self.backbone.fc.in_features
            self.backbone.fc = nn.Sequential(
                nn.Dropout(p=0.4),
                nn.Linear(in_features, 256),
                nn.ReLU(inplace=True),
                nn.BatchNorm1d(256),
                nn.Dropout(p=0.3),
                nn.Linear(256, num_classes)
            )
            self.classifier = self.backbone.fc
        elif backbone_name == "efficientnet_b0":
            weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
            self.backbone = models.efficientnet_b0(weights=weights)
            in_features = self.backbone.classifier[1].in_features
            self.backbone.classifier = nn.Sequential(
                nn.Dropout(p=0.4),
                nn.Linear(in_features, 256),
                nn.SiLU(inplace=True),
                nn.BatchNorm1d(256),
                nn.Dropout(p=0.3),
                nn.Linear(256, num_classes)
            )
            self.classifier = self.backbone.classifier
        else: # Default: MobileNetV3-Large (High speed + high accuracy)
            weights = models.MobileNet_V3_Large_Weights.DEFAULT if pretrained else None
            self.backbone = models.mobilenet_v3_large(weights=weights)
            in_features = self.backbone.classifier[0].in_features
            self.backbone.classifier = nn.Sequential(
                nn.Linear(in_features, 256),
                nn.Hardswish(inplace=True),
                nn.Dropout(p=0.3),
                nn.Linear(256, num_classes)
            )
            self.classifier = self.backbone.classifier

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)

    def freeze_backbone(self):
        """Freezes all backbone feature extraction layers for Stage 1 Transfer Learning."""
        for name, param in self.backbone.named_parameters():
            if "classifier" not in name and "fc" not in name:
                param.requires_grad = False

    def unfreeze_backbone(self):
        """Unfreezes all layers for Stage 2 End-to-End Fine-Tuning."""
        for param in self.backbone.parameters():
            param.requires_grad = True

    def predict_image(self, tensor_img: torch.Tensor, device: str = "cpu") -> tuple:
        """
        Inference helper: returns (predicted_class_name, confidence, good_prob, bad_prob)
        """
        self.eval()
        with torch.no_grad():
            tensor_img = tensor_img.to(device)
            logits = self.forward(tensor_img)
            probs = torch.softmax(logits, dim=1).squeeze(0)
            bad_p = probs[0].item()
            good_p = probs[1].item()
            conf, pred_idx = torch.max(probs, dim=0)
            
            class_map = {0: "BAD", 1: "GOOD"}
            return class_map[pred_idx.item()], conf.item(), good_p, bad_p

# Backward compatibility alias
OnionQualityNet = OnionTransferNet
