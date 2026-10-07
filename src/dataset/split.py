"""
src/dataset/split.py
────────────────────
CELL 3 of Phase 1.

Reads data/splits/cleaned_manifest.csv and produces a stratified
70 / 15 / 15 train / val / test split.

Key guarantee:
  - Fixed seed (from config.RANDOM_SEED) so splits are reproducible.
  - Stratified: each class has the same 70/15/15 ratio.
  - Near-duplicates were already removed by clean.py, so there is NO
    leakage between splits.
  - Outputs: data/splits/train.csv, val.csv, test.csv

Run AFTER clean.py:
    python src/dataset/split.py
"""

import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    SPLITS_DIR,
    TRAIN_RATIO,
    VAL_RATIO,
    TEST_RATIO,
    RANDOM_SEED,
    MIN_IMAGES_PER_CLASS,
)
from src.utils.class_loader import get_class_names


def split_dataset() -> None:
    manifest_path = SPLITS_DIR / "cleaned_manifest.csv"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"cleaned_manifest.csv not found at {manifest_path}\n"
            "Run src/dataset/clean.py first."
        )

    df = pd.read_csv(manifest_path)
    print(f"\n  Total images in manifest: {len(df)}")
    print(f"  Classes found: {sorted(df['class_name'].unique())}\n")

    # Validate all class names
    valid_classes = set(get_class_names())
    bad = set(df["class_name"].unique()) - valid_classes
    if bad:
        raise ValueError(
            f"Manifest contains unknown class names: {bad}\n"
            f"Valid classes: {valid_classes}"
        )

    # Check minimum count per class
    counts = df["class_name"].value_counts()
    print("  Class counts in manifest:")
    for cls in get_class_names():
        n = counts.get(cls, 0)
        flag = "  [LOW - FALLBACK NEEDED]" if n < MIN_IMAGES_PER_CLASS else ""
        print(f"    {cls:<20} {n:>5}{flag}")

    # ── Stratified split: train / temp ─────────────────────────────────────
    # First split: train (70%) vs temp (30%)
    train_df, temp_df = train_test_split(
        df,
        test_size=(VAL_RATIO + TEST_RATIO),
        random_state=RANDOM_SEED,
        stratify=df["class_name"],
    )

    # Second split: val (15%) vs test (15%) from the 30% temp
    # val_ratio within temp = VAL_RATIO / (VAL_RATIO + TEST_RATIO) = 0.5
    val_ratio_within_temp = VAL_RATIO / (VAL_RATIO + TEST_RATIO)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=(1.0 - val_ratio_within_temp),
        random_state=RANDOM_SEED,
        stratify=temp_df["class_name"],
    )

    # ── Add split column and shuffle ────────────────────────────────────────
    train_df = train_df.copy()
    val_df   = val_df.copy()
    test_df  = test_df.copy()

    train_df["split"] = "train"
    val_df["split"]   = "val"
    test_df["split"]  = "test"

    train_df = train_df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
    val_df   = val_df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
    test_df  = test_df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    # ── Save CSVs ───────────────────────────────────────────────────────────
    train_df.to_csv(SPLITS_DIR / "train.csv", index=False)
    val_df.to_csv(SPLITS_DIR / "val.csv", index=False)
    test_df.to_csv(SPLITS_DIR / "test.csv", index=False)

    # ── Summary ─────────────────────────────────────────────────────────────
    print(f"\n  {'Split':<8} {'Total':>7}  Per-class breakdown")
    print("  " + "-" * 60)
    for split_name, split_df in [("train", train_df), ("val", val_df), ("test", test_df)]:
        per_class = split_df["class_name"].value_counts().to_dict()
        breakdown = "  ".join(
            f"{c}:{per_class.get(c, 0)}" for c in get_class_names()
        )
        print(f"  {split_name:<8} {len(split_df):>7}  {breakdown}")

    print(f"\n  SEED used: {RANDOM_SEED}  (never change after this point)")
    print(f"  Saved to : {SPLITS_DIR}\n")
    print("  Next: run src/dataset/bias_check.py")


if __name__ == "__main__":
    split_dataset()
