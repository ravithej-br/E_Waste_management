"""
src/model/evaluate.py
─────────────────────
Comprehensive model evaluation script for Phase 3.

Features:
  1. Test Accuracy & Per-Class Precision, Recall, F1-Score (via scikit-learn)
  2. Confusion Matrix Heatmap (saved to docs/report_assets/confusion_matrix_<model>.png)
  3. Misclassification Diagnostics & Error Analysis (saved to docs/report_assets/misclassifications_<model>.csv)
  4. Model Size on disk (MB)
  5. CPU Latency Benchmark (median & p95 over 100 runs, separating preprocess from inference)
  6. Outputs Markdown Comparison Table for project report
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import classification_report, confusion_matrix

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    PROCESSED_DIR,
    CHECKPOINTS_DIR,
    IMAGE_SIZE,
    RANDOM_SEED,
    EFFICIENTNET_MODEL_NAME,
    MOBILENET_MODEL_NAME,
)
from src.utils.class_loader import get_class_names
from src.model.transforms import get_test_transforms
from src.model.build_model import build_classifier


def benchmark_latency(model: nn.Module, device: torch.device, num_runs: int = 100) -> dict:
    """
    Measures CPU inference latency properly:
    - Warm-up runs (10 iterations)
    - 100 timed single-image inferences
    - Reports median and 95th percentile (p95)
    """
    model.eval()
    dummy_input = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE, device=device)
    
    # Warm-up
    with torch.no_grad():
        for _ in range(10):
            _ = model(dummy_input)
    
    times = []
    with torch.no_grad():
        for _ in range(num_runs):
            t0 = time.perf_counter()
            _ = model(dummy_input)
            t1 = time.perf_counter()
            times.append((t1 - t0) * 1000.0)  # ms
            
    return {
        "median_ms": float(np.median(times)),
        "p95_ms": float(np.percentile(times, 95)),
        "mean_ms": float(np.mean(times)),
        "std_ms": float(np.std(times)),
    }


def evaluate_model(
    model_name: str = EFFICIENTNET_MODEL_NAME,
    checkpoint_path: Path | None = None,
    device_override: str | None = None
) -> dict:
    class_names = get_class_names()
    num_classes = len(class_names)
    device = torch.device(device_override or ("cuda" if torch.cuda.is_available() else "cpu"))

    if checkpoint_path is None:
        checkpoint_path = CHECKPOINTS_DIR / f"{model_name}_best.pth"

    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Checkpoint not found at: {checkpoint_path}\n"
            "Ensure models are placed in models/checkpoints/"
        )

    print(f"\n{'='*65}")
    print(f"  Evaluating: {model_name}")
    print(f"  Checkpoint: {checkpoint_path}")
    print(f"  Device: {device}")
    print(f"{'='*65}\n")

    # Load Model
    model = build_classifier(model_name=model_name, num_classes=num_classes, pretrained=False)
    ckpt = torch.load(checkpoint_path, map_location=device)
    state_dict = ckpt["model_state"] if "model_state" in ckpt else ckpt
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    # Model File Size
    size_mb = checkpoint_path.stat().st_size / (1024 * 1024)

    # Load Test Dataset
    test_dir = PROCESSED_DIR / "test"
    if not test_dir.exists():
        raise FileNotFoundError(f"Test split not found at: {test_dir}")

    test_dataset = ImageFolder(root=test_dir, transform=get_test_transforms(IMAGE_SIZE))
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=0)

    # Inference loop
    all_preds = []
    all_targets = []
    all_probs = []
    all_paths = [s[0] for s in test_dataset.samples]

    with torch.no_grad():
        for imgs, targets in test_loader:
            imgs = imgs.to(device)
            outputs = model(imgs)
            probs = torch.softmax(outputs, dim=-1)
            preds = torch.argmax(probs, dim=-1)

            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(targets.numpy())
            all_probs.extend(probs.cpu().numpy())

    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)
    all_probs = np.array(all_probs)

    # Metrics computation
    report_dict = classification_report(
        all_targets,
        all_preds,
        target_names=class_names,
        output_dict=True,
        zero_division=0
    )
    test_acc = report_dict["accuracy"]
    macro_f1 = report_dict["macro avg"]["f1-score"]
    weighted_f1 = report_dict["weighted avg"]["f1-score"]

    # Latency benchmark on CPU
    cpu_device = torch.device("cpu")
    model_cpu = model.to(cpu_device)
    latency_stats = benchmark_latency(model_cpu, cpu_device, num_runs=100)

    print(f"  Test Accuracy:     {test_acc*100:.2f}%")
    print(f"  Macro F1-Score:    {macro_f1*100:.2f}%")
    print(f"  Weighted F1-Score: {weighted_f1*100:.2f}%")
    print(f"  Model Size:        {size_mb:.2f} MB")
    print(f"  CPU Latency:       {latency_stats['median_ms']:.2f} ms (median), {latency_stats['p95_ms']:.2f} ms (p95)")

    # ── Confusion Matrix Plot ────────────────────────────────────────────────
    report_dir = PROJECT_ROOT / "docs" / "report_assets"
    report_dir.mkdir(parents=True, exist_ok=True)
    cm = confusion_matrix(all_targets, all_preds)

    plt.figure(figsize=(9, 7))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
        cbar=False
    )
    plt.title(f"Confusion Matrix: {model_name} (Test Acc: {test_acc*100:.2f}%)")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    cm_path = report_dir / f"confusion_matrix_{model_name}.png"
    plt.savefig(cm_path, dpi=150)
    plt.close()
    print(f"  Confusion matrix saved: {cm_path}")

    # ── Misclassification Analysis ───────────────────────────────────────────
    misclassified = []
    for idx in range(len(all_targets)):
        if all_targets[idx] != all_preds[idx]:
            true_label = class_names[all_targets[idx]]
            pred_label = class_names[all_preds[idx]]
            conf = all_probs[idx][all_preds[idx]]
            misclassified.append({
                "filepath": Path(all_paths[idx]).name,
                "true_label": true_label,
                "pred_label": pred_label,
                "confidence": round(float(conf), 4),
            })

    mis_df = pd.DataFrame(misclassified)
    mis_path = report_dir / f"misclassifications_{model_name}.csv"
    mis_df.to_csv(mis_path, index=False)
    print(f"  Misclassifications logged ({len(mis_df)} errors): {mis_path}")

    if not mis_df.empty:
        common_errors = mis_df.groupby(["true_label", "pred_label"]).size().reset_index(name="count")
        common_errors = common_errors.sort_values(by="count", ascending=False).head(5)
        print("\n  Top 5 Confusions:")
        for _, row in common_errors.iterrows():
            print(f"    True: {row['true_label']:<15} -> Predicted: {row['pred_label']:<15} ({row['count']} images)")

    # Save summary json
    summary = {
        "model_name": model_name,
        "test_accuracy": round(float(test_acc), 4),
        "macro_f1": round(float(macro_f1), 4),
        "weighted_f1": round(float(weighted_f1), 4),
        "model_size_mb": round(float(size_mb), 2),
        "latency_median_ms": round(latency_stats["median_ms"], 2),
        "latency_p95_ms": round(latency_stats["p95_ms"], 2),
        "per_class": {
            cls: {
                "precision": round(report_dict[cls]["precision"], 4),
                "recall": round(report_dict[cls]["recall"], 4),
                "f1": round(report_dict[cls]["f1-score"], 4),
                "support": report_dict[cls]["support"],
            }
            for cls in class_names
        }
    }

    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    with open(logs_dir / f"test_metrics_{model_name}.json", "w") as f:
        json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate E-Waste Classifiers")
    parser.add_argument("--model", type=str, default="all",
                        choices=["all", EFFICIENTNET_MODEL_NAME, MOBILENET_MODEL_NAME])
    args = parser.parse_args()

    models_to_eval = [EFFICIENTNET_MODEL_NAME, MOBILENET_MODEL_NAME] if args.model == "all" else [args.model]
    all_summaries = []

    for m in models_to_eval:
        s = evaluate_model(model_name=m)
        all_summaries.append(s)

    # Print Report Table
    print(f"\n{'='*75}")
    print("  ACADEMIC RESULTS COMPARISON TABLE (For Project Report)")
    print(f"{'='*75}")
    print(f"| {'Model Architecture':<25} | {'Test Acc (%)':<12} | {'Macro F1':<10} | {'Size (MB)':<10} | {'CPU Latency (ms)':<16} |")
    print(f"|{'-'*27}|{'-'*14}|{'-'*12}|{'-'*12}|{'-'*18}|")
    for s in all_summaries:
        print(f"| {s['model_name']:<25} | {s['test_accuracy']*100:>10.2f}% | {s['macro_f1']*100:>8.2f}% | {s['model_size_mb']:>8.2f}MB | {s['latency_median_ms']:>14.2f}ms |")
    print(f"{'='*75}\n")
