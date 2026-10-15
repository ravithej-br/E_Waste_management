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
    # ══════════════════════════════════════════════════════════════════════
    # DS1 — akshat103/e-waste-image-dataset  (30 images per class)
    # Downloaded to: ~/.cache/kagglehub/datasets/akshat103/e-waste-image-dataset/versions/1
    # ══════════════════════════════════════════════════════════════════════
    "Battery":          "battery",         # 30 imgs → battery
    "Keyboard":         "keyboard",        # 30 imgs → keyboard
    "Mobile":           "mobile_phone",    # 30 imgs → mobile_phone
    "PCB":              "pcb",             # 30 imgs → pcb
    "Television":       "monitor_crt",     # 30 imgs → monitor_crt (closest match; old CRT TVs)
    "Mouse":            "other",           # 30 imgs → other (no mouse class)
    "Microwave":        "other",           # 30 imgs → other (appliance, not e-waste class)
    "Printer":          "other",           # 30 imgs → other (no printer class)
    "Player":           "other",           # 30 imgs → other (media player)
    "Washing Machine":  "other",           # 30 imgs → other (appliance)

    # ══════════════════════════════════════════════════════════════════════
    # DS4 — aryaminus/electronic-components  (10,990 images, 36 classes)
    # Downloaded to: ~/.cache/kagglehub/datasets/aryaminus/electronic-components/versions/1
    # Strategy: keep only components that visually represent a PCB/board.
    # ══════════════════════════════════════════════════════════════════════
    "Integrated-micro-circuit": "pcb",    # 470 imgs — IC chips on boards
    "microchip":                "pcb",    # 461 imgs — chips
    "microprocessor":           "pcb",    # 457 imgs — CPUs
    "memory-chip":              "pcb",    # 297 imgs — RAM/ROM chips
    # ── Drop rest (too granular / not visually e-waste) ───────────────────
    "junction-transistor":      "DROP",
    "LED":                      "DROP",
    "potentiometer":            "DROP",
    "relay":                    "DROP",
    "limiter-clipper":          "DROP",
    "semi-conductor":           "DROP",
    "electric-relay":           "DROP",
    "heat-sink":                "DROP",
    "semiconductor-diode":      "DROP",
    "step-down-transformer":    "DROP",
    "Electrolytic-capacitor":   "DROP",
    "filament":                 "DROP",
    "armature":                 "DROP",
    "pulse-generator":          "DROP",
    "solenoid":                 "DROP",
    "PNP-transistor":           "DROP",
    "Bypass-capacitor":         "DROP",
    "clip-lead":                "DROP",
    "attenuator":               "DROP",
    "jumper-cable":             "DROP",
    "potential-divider":        "DROP",
    "cartridge-fuse":           "DROP",
    "rheostat":                 "DROP",
    "stabilizer":               "DROP",
    "step-up-transformer":      "DROP",
    "transistor":               "DROP",
    "induction-coil":           "DROP",
    "omni-directional-antenna": "DROP",
    "local-oscillator":         "DROP",
    "shunt":                    "DROP",
    "multiplexer":              "DROP",
    "light-circuit":            "DROP",

    # ══════════════════════════════════════════════════════════════════════
    # Own phone photos (team-collected — place in data/raw/downloads/own/)
    # ══════════════════════════════════════════════════════════════════════
    "own_battery":       "battery",
    "own_cfl":           "cfl_bulb",        # NEEDED — collect 80+ photos
    "own_crt":           "monitor_crt",     # NEEDED — collect 50+ photos
    "own_mobile":        "mobile_phone",
    "own_keyboard":      "keyboard",
    "own_pcb":           "pcb",
    "own_other":         "other",
}

# ─────────────────────────────────────────────────────────────────────────────
# Actual download locations (kagglehub caches here automatically)
# ─────────────────────────────────────────────────────────────────────────────
import os

_KAGGLE_CACHE = Path(os.path.expanduser("~")) / ".cache" / "kagglehub" / "datasets"

DATASET_PATHS = {
    "DS1": _KAGGLE_CACHE / "akshat103" / "e-waste-image-dataset" / "versions" / "1",
    "DS4": _KAGGLE_CACHE / "aryaminus" / "electronic-components" / "versions" / "1",
    "OWN": RAW_DIR / "downloads" / "own",   # team-collected phone photos
}


def ingest(dry_run: bool = False) -> None:
    valid_classes = set(get_class_names())
    copied = 0
    dropped = 0
    unknown = []

    for ds_id, ds_root in DATASET_PATHS.items():
        if not ds_root.exists():
            print(f"  [SKIP] {ds_id} path not found: {ds_root}")
            continue
        print(f"\n  Scanning {ds_id}: {ds_root}")

        for src_class_dir in ds_root.rglob("*"):
            if not src_class_dir.is_dir():
                continue
            folder_name = src_class_dir.name
            if folder_name not in CLASS_MAPPING:
                continue
            target_class = CLASS_MAPPING[folder_name]

            if target_class == "DROP":
                img_count = sum(1 for f in src_class_dir.iterdir()
                                if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
                if img_count:
                    print(f"    [DROP] {folder_name}  ({img_count} images skipped)")
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
                # Unique name: <DS_ID>_<source_class>_<original_name>
                dest_name = f"{ds_id}_{folder_name}_{img_path.name}"
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

    print(f"\nDataset sources:")
    for ds_id, path in DATASET_PATHS.items():
        status = "FOUND" if path.exists() else "NOT FOUND"
        print(f"  {ds_id}: {path}  [{status}]")
    print(f"\nDestination: {RAW_DIR}\n")
    ingest(dry_run=args.dry_run)
    print("\nDone. Next: run src/dataset/clean.py")

