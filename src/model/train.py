"""
src/model/train.py
──────────────────
Two-stage transfer learning training script for E-Waste classification.
Supports EfficientNet-B0 and MobileNetV3-Small baselines.

Features:
  - Stage 1: Frozen backbone, train head (5 epochs, lr=1e-3)
  - Stage 2: Fine-tune top blocks (10 epochs, lr=1e-4) with Cosine Annealing LR
  - Label smoothing (default 0.1) & optional class weights
  - Automatic Mixed Precision (AMP) with GradScaler
  - Gradient clipping (max norm 1.0)
  - Early stopping with patience 5
  - Checkpoint save / resume (recovers from Colab timeouts)
  - Metrics logged to logs/training_metrics_<model_name>.csv
  - Training curve plot saved to logs/curves_<model_name>.png
"""

import os
import sys
import time
import math
import random
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    PROCESSED_DIR,
    CHECKPOINTS_DIR,
    MODELS_DIR,
    IMAGE_SIZE,
    BATCH_SIZE,
    NUM_WORKERS,
    STAGE1_EPOCHS,
    STAGE1_LR,
    STAGE2_EPOCHS,
    STAGE2_LR,
    WEIGHT_DECAY,
    LABEL_SMOOTHING,
    EARLY_STOP_PATIENCE,
    GRAD_CLIP_NORM,
    USE_AMP,
    RANDOM_SEED,
    EFFICIENTNET_MODEL_NAME,
    MOBILENET_MODEL_NAME,
)
from src.utils.class_loader import get_class_names
from src.model.transforms import get_train_transforms, get_val_transforms
from src.model.build_model import build_classifier, freeze_backbone, unfreeze_last_blocks, count_parameters


def set_seed(seed: int = RANDOM_SEED):
    """Ensure exact reproducibility across runs."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def calculate_class_weights(dataset: ImageFolder, device: torch.device) -> torch.Tensor:
    """
    Compute inverse frequency class weights to balance loss:
    weight[c] = total_samples / (num_classes * count[c])
    """
    targets = [target for _, target in dataset.samples]
    class_counts = np.bincount(targets)
    total_samples = len(targets)
    num_classes = len(class_counts)
    
    weights = total_samples / (num_classes * class_counts.astype(np.float32))
    return torch.tensor(weights, dtype=torch.float32, device=device)


def train_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    scaler: torch.amp.GradScaler | None,
    device: torch.device,
    use_amp: bool = True
) -> tuple[float, float]:
    """Train for one epoch, returning (avg_loss, accuracy)."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, targets in dataloader:
        images = images.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)

        optimizer.zero_grad(set_to_none=True)

        if use_amp and device.type == "cuda" and scaler is not None:
            with torch.amp.autocast(device_type="cuda", dtype=torch.float16):
                outputs = model(images)
                loss = criterion(outputs, targets)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=GRAD_CLIP_NORM)
            scaler.step(optimizer)
            scaler.update()
        else:
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=GRAD_CLIP_NORM)
            optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, preds = torch.max(outputs, 1)
        correct += (preds == targets).sum().item()
        total += targets.size(0)

    epoch_loss = running_loss / total
    epoch_acc = correct / total
    return epoch_loss, epoch_acc


@torch.no_grad()
def evaluate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    use_amp: bool = True
) -> tuple[float, float]:
    """Evaluate on validation set, returning (avg_loss, accuracy)."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, targets in dataloader:
        images = images.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)

        if use_amp and device.type == "cuda":
            with torch.amp.autocast(device_type="cuda", dtype=torch.float16):
                outputs = model(images)
                loss = criterion(outputs, targets)
        else:
            outputs = model(images)
            loss = criterion(outputs, targets)

        running_loss += loss.item() * images.size(0)
        _, preds = torch.max(outputs, 1)
        correct += (preds == targets).sum().item()
        total += targets.size(0)

    val_loss = running_loss / total
    val_acc = correct / total
    return val_loss, val_acc


def plot_curves(metrics_csv_path: Path, output_png_path: Path, model_name: str) -> None:
    """Plot and save training and validation loss and accuracy curves."""
    df = pd.read_csv(metrics_csv_path)
    
    plt.figure(figsize=(12, 5))
    
    # Loss subplot
    plt.subplot(1, 2, 1)
    plt.plot(df["epoch"], df["train_loss"], label="Train Loss", marker="o", markersize=3)
    plt.plot(df["epoch"], df["val_loss"], label="Val Loss", marker="s", markersize=3)
    plt.title(f"{model_name} - Loss Curve")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Accuracy subplot
    plt.subplot(1, 2, 2)
    plt.plot(df["epoch"], df["train_acc"] * 100, label="Train Acc (%)", marker="o", markersize=3)
    plt.plot(df["epoch"], df["val_acc"] * 100, label="Val Acc (%)", marker="s", markersize=3)
    plt.title(f"{model_name} - Accuracy Curve")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy (%)")
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()
    plt.savefig(output_png_path, dpi=150)
    plt.close()
    print(f"  Training curves saved to: {output_png_path}")


def run_training(
    model_name: str = EFFICIENTNET_MODEL_NAME,
    stage1_epochs: int = STAGE1_EPOCHS,
    stage2_epochs: int = STAGE2_EPOCHS,
    batch_size: int = BATCH_SIZE,
    use_augmentation: bool = True,
    label_smoothing: float = LABEL_SMOOTHING,
    use_class_weights: bool = True,
    resume: bool = False,
    device_override: str | None = None
) -> Path:
    """
    Executes the full two-stage training loop.
    Returns path to the best saved model weights.
    """
    set_seed(RANDOM_SEED)
    class_names = get_class_names()
    num_classes = len(class_names)
    
    # Device setup
    if device_override:
        device = torch.device(device_override)
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n{'='*60}")
    print(f"  Starting Training: {model_name}")
    print(f"  Device: {device} | Mixed Precision (AMP): {USE_AMP and device.type == 'cuda'}")
    print(f"  Classes ({num_classes}): {class_names}")
    print(f"{'='*60}\n")

    # Paths
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
    
    metrics_csv = logs_dir / f"training_metrics_{model_name}.csv"
    curves_png = logs_dir / f"curves_{model_name}.png"
    best_model_path = CHECKPOINTS_DIR / f"{model_name}_best.pth"
    last_ckpt_path = CHECKPOINTS_DIR / f"{model_name}_last.pth"

    # Datasets and Loaders
    train_dir = PROCESSED_DIR / "train"
    val_dir = PROCESSED_DIR / "val"
    if not train_dir.exists() or not val_dir.exists():
        raise FileNotFoundError(
            f"Processed data not found at {PROCESSED_DIR}.\n"
            "Run src/dataset/organise_folders.py first!"
        )

    train_dataset = ImageFolder(root=train_dir, transform=get_train_transforms(IMAGE_SIZE, use_augmentation))
    val_dataset = ImageFolder(root=val_dir, transform=get_val_transforms(IMAGE_SIZE))
    
    # Ensure ImageFolder class ordering matches classes.json
    assert train_dataset.classes == class_names, (
        f"Folder names {train_dataset.classes} do not match classes.json {class_names}"
    )

    # Windows DataLoader compatibility
    workers = 0 if sys.platform.startswith("win") else NUM_WORKERS
    pin_mem = True if device.type == "cuda" else False

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=workers,
        pin_memory=pin_mem
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=workers,
        pin_memory=pin_mem
    )

    print(f"  Train samples: {len(train_dataset)} | Val samples: {len(val_dataset)}")

    # Class weighting
    class_weights = None
    if use_class_weights:
        class_weights = calculate_class_weights(train_dataset, device)
        print(f"  Applied class weights to loss function to mitigate class imbalance.")

    criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=label_smoothing)

    # Model initialization
    model = build_classifier(model_name=model_name, num_classes=num_classes, pretrained=True)
    model.to(device)

    scaler = torch.amp.GradScaler("cuda") if (USE_AMP and device.type == "cuda") else None

    # Checkpoint resume check
    start_epoch = 1
    best_val_loss = float("inf")
    best_val_acc = 0.0
    history = []

    if resume and last_ckpt_path.exists():
        print(f"  [RESUME] Loading last checkpoint from: {last_ckpt_path}")
        ckpt = torch.load(last_ckpt_path, map_location=device)
        model.load_state_dict(ckpt["model_state"])
        start_epoch = ckpt["epoch"] + 1
        best_val_loss = ckpt.get("best_val_loss", float("inf"))
        best_val_acc = ckpt.get("best_val_acc", 0.0)
        print(f"  [RESUME] Continuing from epoch {start_epoch} (Best Val Loss: {best_val_loss:.4f})")

    total_epochs = stage1_epochs + stage2_epochs
    patience_counter = 0

    # ── STAGE 1: Freeze Backbone ─────────────────────────────────────────────
    if start_epoch <= stage1_epochs:
        print("\n" + "="*50)
        print(f"  STAGE 1: Training classifier head only ({stage1_epochs} epochs, lr={STAGE1_LR})")
        print("="*50)
        freeze_backbone(model)
        tot_p, tr_p = count_parameters(model)
        print(f"  Trainable parameters: {tr_p:,} / {tot_p:,} ({tr_p/tot_p*100:.2f}%)")

        optimizer = torch.optim.AdamW(
            [p for p in model.parameters() if p.requires_grad],
            lr=STAGE1_LR,
            weight_decay=WEIGHT_DECAY
        )

        for epoch in range(start_epoch, stage1_epochs + 1):
            t0 = time.time()
            tr_loss, tr_acc = train_one_epoch(model, train_loader, criterion, optimizer, scaler, device, USE_AMP)
            v_loss, v_acc = evaluate(model, val_loader, criterion, device, USE_AMP)
            elapsed = time.time() - t0

            print(f"  Epoch {epoch:02d}/{total_epochs:02d} [Stage 1] ({elapsed:.1f}s) | "
                  f"Train Loss: {tr_loss:.4f} Acc: {tr_acc*100:.2f}% | "
                  f"Val Loss: {v_loss:.4f} Acc: {v_acc*100:.2f}%")

            history.append({
                "epoch": epoch,
                "stage": 1,
                "train_loss": tr_loss,
                "train_acc": tr_acc,
                "val_loss": v_loss,
                "val_acc": v_acc,
                "lr": STAGE1_LR,
            })

            # Save best checkpoint
            if v_loss < best_val_loss:
                best_val_loss = v_loss
                best_val_acc = v_acc
                torch.save({
                    "epoch": epoch,
                    "model_state": model.state_dict(),
                    "val_loss": v_loss,
                    "val_acc": v_acc,
                    "model_name": model_name,
                    "classes": class_names,
                }, best_model_path)
                print(f"    --> Saved best checkpoint: Val Loss = {v_loss:.4f}")

            # Save last checkpoint for crash recovery
            torch.save({
                "epoch": epoch,
                "model_state": model.state_dict(),
                "best_val_loss": best_val_loss,
                "best_val_acc": best_val_acc,
            }, last_ckpt_path)

    # ── STAGE 2: Fine-tuning top blocks ──────────────────────────────────────
    stage2_start = max(start_epoch, stage1_epochs + 1)
    if stage2_start <= total_epochs:
        print("\n" + "="*50)
        print(f"  STAGE 2: Fine-tuning top blocks ({stage2_epochs} epochs, lr={STAGE2_LR} with Cosine LR)")
        print("="*50)
        unfreeze_last_blocks(model, model_name=model_name)
        tot_p, tr_p = count_parameters(model)
        print(f"  Trainable parameters: {tr_p:,} / {tot_p:,} ({tr_p/tot_p*100:.2f}%)")

        optimizer = torch.optim.AdamW(
            [p for p in model.parameters() if p.requires_grad],
            lr=STAGE2_LR,
            weight_decay=WEIGHT_DECAY
        )
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=stage2_epochs,
            eta_min=1e-6
        )

        for epoch in range(stage2_start, total_epochs + 1):
            t0 = time.time()
            current_lr = optimizer.param_groups[0]["lr"]
            tr_loss, tr_acc = train_one_epoch(model, train_loader, criterion, optimizer, scaler, device, USE_AMP)
            v_loss, v_acc = evaluate(model, val_loader, criterion, device, USE_AMP)
            scheduler.step()
            elapsed = time.time() - t0

            print(f"  Epoch {epoch:02d}/{total_epochs:02d} [Stage 2] ({elapsed:.1f}s) | "
                  f"Train Loss: {tr_loss:.4f} Acc: {tr_acc*100:.2f}% | "
                  f"Val Loss: {v_loss:.4f} Acc: {v_acc*100:.2f}% | lr: {current_lr:.1e}")

            history.append({
                "epoch": epoch,
                "stage": 2,
                "train_loss": tr_loss,
                "train_acc": tr_acc,
                "val_loss": v_loss,
                "val_acc": v_acc,
                "lr": current_lr,
            })

            # Early stopping check
            if v_loss < best_val_loss:
                best_val_loss = v_loss
                best_val_acc = v_acc
                patience_counter = 0
                torch.save({
                    "epoch": epoch,
                    "model_state": model.state_dict(),
                    "val_loss": v_loss,
                    "val_acc": v_acc,
                    "model_name": model_name,
                    "classes": class_names,
                }, best_model_path)
                print(f"    --> Saved best checkpoint: Val Loss = {v_loss:.4f} Acc = {v_acc*100:.2f}%")
            else:
                patience_counter += 1
                print(f"    (Early stop counter: {patience_counter}/{EARLY_STOP_PATIENCE})")
                if patience_counter >= EARLY_STOP_PATIENCE:
                    print(f"\n  [EARLY STOP] Validation loss did not improve for {EARLY_STOP_PATIENCE} epochs.")
                    break

            # Save last checkpoint
            torch.save({
                "epoch": epoch,
                "model_state": model.state_dict(),
                "best_val_loss": best_val_loss,
                "best_val_acc": best_val_acc,
            }, last_ckpt_path)

    # Save metrics to CSV and plot curves
    if history:
        metrics_df = pd.DataFrame(history)
        metrics_df.to_csv(metrics_csv, index=False)
        print(f"\n  Per-epoch metrics saved to: {metrics_csv}")
        plot_curves(metrics_csv, curves_png, model_name=model_name)

    print(f"\n{'='*60}")
    print(f"  Training Complete: {model_name}")
    print(f"  Best Val Loss: {best_val_loss:.4f} | Best Val Accuracy: {best_val_acc*100:.2f}%")
    print(f"  Best model weights: {best_model_path}")
    print(f"{'='*60}\n")

    return best_model_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train E-Waste Classifier")
    parser.add_argument("--model", type=str, default=EFFICIENTNET_MODEL_NAME,
                        choices=[EFFICIENTNET_MODEL_NAME, MOBILENET_MODEL_NAME],
                        help="Model architecture to train")
    parser.add_argument("--stage1-epochs", type=int, default=STAGE1_EPOCHS)
    parser.add_argument("--stage2-epochs", type=int, default=STAGE2_EPOCHS)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--no-augmentation", action="store_true",
                        help="Disable data augmentation for ablation testing")
    parser.add_argument("--no-smoothing", action="store_true",
                        help="Set label smoothing to 0 for ablation testing")
    parser.add_argument("--no-class-weights", action="store_true",
                        help="Disable class weighting in loss")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from last checkpoint if available")
    args = parser.parse_args()

    smoothing = 0.0 if args.no_smoothing else LABEL_SMOOTHING
    run_training(
        model_name=args.model,
        stage1_epochs=args.stage1_epochs,
        stage2_epochs=args.stage2_epochs,
        batch_size=args.batch_size,
        use_augmentation=not args.no_augmentation,
        label_smoothing=smoothing,
        use_class_weights=not args.no_class_weights,
        resume=args.resume
    )
