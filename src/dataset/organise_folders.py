"""
src/dataset/organise_folders.py
───────────────────────────────
CELL 5 of Phase 1.

Copies images from raw/<class>/ into the processed folder structure
that PyTorch's ImageFolder loader expects:

    data/processed/train/<class_name>/<image.jpg>
    data/processed/val/<class_name>/<image.jpg>
    data/processed/test/<class_name>/<image.jpg>

Reads from the CSV files produced by split.py.

Run AFTER split.py:
    python src/dataset/organise_folders.py
"""

import shutil
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import SPLITS_DIR, PROCESSED_DIR
from src.utils.class_loader import get_class_names


def organise() -> None:
    class_names = get_class_names()

    for split in ["train", "val", "test"]:
        csv_path = SPLITS_DIR / f"{split}.csv"
        if not csv_path.exists():
            print(f"  [SKIP] {csv_path} not found.")
            continue

        df = pd.read_csv(csv_path)
        print(f"\n  Organising {split}: {len(df)} images")

        for _, row in tqdm(df.iterrows(), total=len(df), desc=f"  {split}"):
            src = Path(row["filepath"])
            cls = row["class_name"]
            dest_dir = PROCESSED_DIR / split / cls
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / src.name
            if not dest.exists():
                shutil.copy2(src, dest)

    # Print final counts
    print("\n  --- Final processed folder counts ---")
    for split in ["train", "val", "test"]:
        print(f"\n  [{split}]")
        for cls in class_names:
            folder = PROCESSED_DIR / split / cls
            n = len(list(folder.glob("*.*"))) if folder.exists() else 0
            print(f"    {cls:<20} {n:>5} images")

    print(f"\n  Done. Processed data at: {PROCESSED_DIR}")
    print("  Next: open notebooks/phase2_training.ipynb in Google Colab.")


if __name__ == "__main__":
    organise()
