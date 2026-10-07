"""
src/dataset/ingest.py
─────────────────────
CELL 1 of Phase 1 notebook / standalone script.

Reorganises downloaded raw images from multiple datasets into a single flat
structure under data/raw/<class_name>/, applying the class mapping you
filled in from class_mapping_template.txt.

Usage:
    python src/dataset/ingest.py

Prerequisites:
    - Download datasets manually from Kaggle / Hugging Face.
    - Unzip them somewhere under data/raw/downloads/.
    - Fill in CLASS_MAPPING below from your class_mapping_template.txt.
"""

import shutil
import sys
from pathlib import Path

# ─── Add project root to path ────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import RAW_DIR
from src.utils.class_loader import get_class_names

# ─────────────────────────────────────────────────────────────────────────────
# FILL IN THIS MAPPING after checking actual folder names in your downloads.
# Key   = source folder name (exactly as it appears on disk, case-sensitive)
# Value = target class name  (must be one of the 7 classes in classes.json)
#         or "DROP"          (skip this class entirely)
# ─────────────────────────────────────────────────────────────────────────────
CLASS_MAPPING = {
    # ── DS1 examples (REPLACE with real names after download) ─────────────
    "Battery":          "battery",
    "CRT_Monitor":      "monitor_crt",
    "CFL":              "cfl_bulb",
    "Keyboard":         "keyboard",
    "Mobile":           "mobile_phone",
    "PCB":              "pcb",
    "Laptop":           "DROP",        # no laptop class; drop or add if you want

    # ── DS2 examples (REPLACE) ─────────────────────────────────────────────
    "battery":          "battery",
    "electronics":      "other",

    # ── DS4 examples (REPLACE) ─────────────────────────────────────────────
    "PCB_Board":        "pcb",
    "Resistor":         "DROP",
    "Capacitor":        "DROP",

    # ── Own photos ─────────────────────────────────────────────────────────
    "phone_photos":     "mobile_phone",
    "battery_photos":   "battery",
}

# ─────────────────────────────────────────────────────────────────────────────
# Source: where your unzipped downloads live
# Structure expected: DOWNLOAD_ROOT/<any_subfolder>/<class_folder>/<image.jpg>
# ─────────────────────────────────────────────────────────────────────────────
DOWNLOAD_ROOT = RAW_DIR / "downloads"


def ingest(dry_run: bool = False) -> None:
    valid_classes = set(get_class_names())
    copied = 0
    dropped = 0
    unknown = []

    for src_class_dir in DOWNLOAD_ROOT.rglob("*"):
        if not src_class_dir.is_dir():
            continue

        folder_name = src_class_dir.name
        if folder_name not in CLASS_MAPPING:
            continue

        target_class = CLASS_MAPPING[folder_name]

        if target_class == "DROP":
            img_count = sum(1 for f in src_class_dir.iterdir()
                            if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
            print(f"  [DROP] {folder_name}  ({img_count} images skipped)")
            dropped += img_count
            continue

        if target_class not in valid_classes:
            unknown.append((folder_name, target_class))
            continue

        dest_dir = RAW_DIR / target_class
        dest_dir.mkdir(parents=True, exist_ok=True)

        for img_path in src_class_dir.iterdir():
            if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                continue
            # Give each image a unique name: <source_class>_<original_name>
            dest_name = f"{folder_name}_{img_path.name}"
            dest_path = dest_dir / dest_name
            if not dry_run:
                shutil.copy2(img_path, dest_path)
            copied += 1

    print(f"\n  Copied : {copied}")
    print(f"  Dropped: {dropped}")
    if unknown:
        print(f"\n  [WARN] Unknown target classes (fix CLASS_MAPPING):")
        for src, tgt in unknown:
            print(f"         {src!r} -> {tgt!r}")
    if dry_run:
        print("\n  [DRY RUN] No files were actually copied.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest raw datasets into class folders.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would happen without copying files.")
    args = parser.parse_args()

    print(f"\nIngesting from: {DOWNLOAD_ROOT}")
    print(f"Destination   : {RAW_DIR}\n")
    ingest(dry_run=args.dry_run)
    print("\nDone. Next: run src/dataset/clean.py")
