"""
src/dataset/bias_check.py
─────────────────────────
CELL 4 of Phase 1.

Checks for common dataset biases:
  1. Source bias  – does one class come almost entirely from one dataset?
  2. Size bias    – are most images from one resolution bucket?
  3. Class imbalance – computes imbalance ratio and suggests remedy.
  4. Generates a bar chart of class counts saved to docs/report_assets/.

Run AFTER split.py:
    python src/dataset/bias_check.py
"""

import sys
from pathlib import Path
from collections import Counter

import matplotlib
matplotlib.use("Agg")   # headless – no GUI needed
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import SPLITS_DIR, RAW_DIR
from src.utils.class_loader import get_class_names

REPORT_DIR = PROJECT_ROOT / "docs" / "report_assets"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def check_bias() -> None:
    train_csv = SPLITS_DIR / "train.csv"
    if not train_csv.exists():
        raise FileNotFoundError("train.csv not found. Run split.py first.")

    train_df = pd.read_csv(train_csv)
    class_names = get_class_names()

    # ── 1. Class counts and imbalance ratio ─────────────────────────────────
    counts = train_df["class_name"].value_counts()
    max_count = counts.max()
    min_count = counts.min()
    ratio = max_count / max(min_count, 1)

    print("\n  --- Class Imbalance (TRAIN split) ---")
    for cls in class_names:
        n = counts.get(cls, 0)
        bar = "#" * (n // max(max_count // 40, 1))
        print(f"    {cls:<20} {n:>5}  {bar}")

    print(f"\n  Max/Min imbalance ratio: {ratio:.2f}x")
    if ratio > 5:
        print("  [WARN] Ratio > 5. Strong imbalance detected.")
        print("  Remedy options:")
        print("    A) Use class weights in loss function (recommended first).")
        print("       weights[i] = total_samples / (num_classes * count[i])")
        print("    B) Oversample minority classes with torchvision transforms.")
        print("    C) Collect more images for under-represented classes.")
    elif ratio > 2:
        print("  [NOTE] Mild imbalance. Class weights in loss function are enough.")
    else:
        print("  [OK] Imbalance ratio is acceptable (< 2x).")

    # ── 2. Source bias ───────────────────────────────────────────────────────
    # Infer source from filename prefix (e.g., "Battery_xxx.jpg" -> "Battery")
    print("\n  --- Source Bias Check ---")
    print("  (Checks if a class has images from only one source prefix)")
    for cls in class_names:
        class_rows = train_df[train_df["class_name"] == cls]
        if class_rows.empty:
            continue
        prefixes = class_rows["filepath"].apply(
            lambda p: "_".join(Path(p).stem.split("_")[:1])  # first word of filename
        )
        prefix_counts = Counter(prefixes)
        dominant = prefix_counts.most_common(1)[0]
        pct = 100 * dominant[1] / max(len(class_rows), 1)
        flag = "  [BIAS RISK]" if pct > 80 else ""
        print(f"    {cls:<20} dominant prefix: {dominant[0]!r} ({pct:.0f}%){flag}")
    print("  If [BIAS RISK]: collect images from varied sources or backgrounds.")

    # ── 3. Resolution check ──────────────────────────────────────────────────
    print("\n  --- Image Resolution Sample (first 50 per class) ---")
    for cls in class_names:
        class_rows = train_df[train_df["class_name"] == cls].head(50)
        widths, heights = [], []
        for _, row in class_rows.iterrows():
            try:
                with Image.open(row["filepath"]) as img:
                    widths.append(img.width)
                    heights.append(img.height)
            except Exception:
                pass
        if widths:
            print(f"    {cls:<20} avg {sum(widths)//len(widths)}x"
                  f"{sum(heights)//len(heights)}  "
                  f"min {min(widths)}x{min(heights)}  "
                  f"max {max(widths)}x{max(heights)}")

    # ── 4. Class count bar chart ──────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = [counts.get(c, 0) for c in class_names]
    ax.bar(class_names, bars, color="steelblue", edgecolor="white")
    ax.axhline(y=80, color="red", linestyle="--", linewidth=1,
               label=f"Min threshold ({80})")
    ax.set_title("Training Set Class Distribution")
    ax.set_xlabel("Class")
    ax.set_ylabel("Image Count")
    ax.legend()
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    chart_path = REPORT_DIR / "class_distribution.png"
    plt.savefig(chart_path, dpi=150)
    plt.close()
    print("  Add this chart to your report (Section: Dataset -> Class Distribution).\n")


if __name__ == "__main__":
    check_bias()
