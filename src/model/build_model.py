"""
src/model/build_model.py
─────────────────────────
Factory for building EfficientNet-B0 and MobileNetV3-Small classifiers using timm.
Includes functions for 2-stage transfer learning:
  - Stage 1: Freeze backbone, train only the newly initialized classifier head
  - Stage 2: Unfreeze the last convolutional blocks for fine-tuning
"""

import sys
from pathlib import Path
import torch
import torch.nn as nn
import timm

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import EFFICIENTNET_MODEL_NAME, MOBILENET_MODEL_NAME


def build_classifier(
    model_name: str = EFFICIENTNET_MODEL_NAME,
    num_classes: int = 7,
    pretrained: bool = True,
    dropout: float = 0.2
) -> nn.Module:
    """
    Builds a pretrained backbone model from timm and replaces the classifier head.
    
    Args:
        model_name: "efficientnet_b0" or "mobilenetv3_small_100"
        num_classes: number of output target classes (7)
        pretrained: whether to load ImageNet pretrained weights
        dropout: dropout probability in the classification head
    """
    model = timm.create_model(
        model_name,
        pretrained=pretrained,
        num_classes=num_classes,
        drop_rate=dropout
    )
    return model


def freeze_backbone(model: nn.Module) -> None:
    """
    Stage 1: Freeze all backbone parameters.
    Only the final classification head (classifier / fc) will have requires_grad=True.
    """
    # Freeze everything first
    for param in model.parameters():
        param.requires_grad = False
    
    # Unfreeze only the classifier head
    head = model.get_classifier()
    if isinstance(head, nn.Module):
        for param in head.parameters():
            param.requires_grad = True
    elif isinstance(head, nn.Parameter):
        head.requires_grad = True
    else:
        # Fallback for standard attribute names if get_classifier is not module
        for name, param in model.named_parameters():
            if "classifier" in name or "head" in name or "fc" in name:
                param.requires_grad = True


def unfreeze_last_blocks(model: nn.Module, model_name: str = EFFICIENTNET_MODEL_NAME) -> None:
    """
    Stage 2: Unfreeze the top layers/blocks of the backbone and classifier.
    Early feature extraction layers (low-level edges/textures) remain frozen.
    """
    if "efficientnet" in model_name:
        # For EfficientNet, blocks 5 and 6 and conv_head are top-level
        for name, param in model.named_parameters():
            if any(block in name for block in ["blocks.5", "blocks.6", "conv_head", "bn2", "classifier"]):
                param.requires_grad = True
            else:
                param.requires_grad = False
    elif "mobilenetv3" in model_name:
        # For MobileNetV3, unfreeze top blocks (blocks 10-11 / conv_head / classifier)
        for name, param in model.named_parameters():
            if any(part in name for part in ["blocks.4", "blocks.5", "conv_head", "classifier"]):
                param.requires_grad = True
            else:
                param.requires_grad = False
    else:
        # Generic fallback: unfreeze all parameters for fine-tuning
        for param in model.parameters():
            param.requires_grad = True


def count_parameters(model: nn.Module) -> tuple[int, int]:
    """
    Returns (total_params, trainable_params)
    """
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable
