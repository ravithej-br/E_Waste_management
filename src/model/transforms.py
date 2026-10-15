"""
src/model/transforms.py
────────────────────────
PyTorch image transforms for training, validation, and testing.

Rules enforced:
  - 224x224 resolution (EfficientNet-B0 and MobileNetV3 standard)
  - Train: Random horizontal flip, slight rotation, color jitter, ImageNet normalization
  - Val/Test: Deterministic resize and ImageNet normalization (NO data augmentation)
"""

import sys
from pathlib import Path
from torchvision import transforms

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import IMAGE_SIZE, IMAGENET_MEAN, IMAGENET_STD


def get_train_transforms(image_size: int = IMAGE_SIZE, use_augmentation: bool = True) -> transforms.Compose:
    """
    Transforms for the training split.
    If use_augmentation is False, acts as ablation baseline (transforms without augmentation).
    """
    if use_augmentation:
        return transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])
    else:
        return transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])


def get_val_transforms(image_size: int = IMAGE_SIZE) -> transforms.Compose:
    """
    Transforms for validation. Deterministic, no random data augmentation.
    """
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def get_test_transforms(image_size: int = IMAGE_SIZE) -> transforms.Compose:
    """
    Transforms for test split and inference. Deterministic.
    """
    return get_val_transforms(image_size=image_size)
