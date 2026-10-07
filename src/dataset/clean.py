"""
src/dataset/clean.py
────────────────────
CELL 2 of Phase 1.

Steps performed on data/raw/<class>/:
  1. Remove files that are not valid images (corrupt check via PIL).
  2. Remove near-duplicate images using perceptual hashing (pHash).
     Near-duplicates are detected BEFORE any split to prevent data leakage.
  3. Report class balance and flag under-represented classes.
  4. Save a cleaned manifest CSV: data/splits/cleaned_manifest.csv

Run AFTER ingest.py:
    python src/dataset/clean.py

Optional flags:
    --hash-threshold 8    perceptual hash Hamming distance threshold (default 8)
    --dry-run             report what would be removed without deleting
"""

import argparse
import csv
import sys
from pathlib import Path

import imagehash
from PIL import Image, UnidentifiedImageError
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import RAW_DIR, SPLITS_DIR, HASH_THRESHOLD, MIN_IMAGES_PER_CLASS
from src.utils.class_loader import get_class_names

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


# ─────────────────────────────────────────────────────────────────────────────
# 1. Corrupt image removal
# ─────────────────────────────────────────────────────────────────────────────

def remove_corrupt(class_dir: Path, dry_run: bool) -> list:
    """Return list of paths removed due to corruption."""
    removed = []
    for img_path in class_dir.iterdir():
        if img_path.suffix.lower() not in VALID_EXTENSIONS:
            continue
        try:
            with Image.open(img_path) as img:
                img.verify()          # checks file header
            # Re-open to check pixel data (verify() closes the file)
            with Image.open(img_path) as img:
                img.load()
        except (UnidentifiedImageError, Exception):
            removed.append(img_path)
            if not dry_run:
                img_path.unlink()
    return removed


# ─────────────────────────────────────────────────────────────────────────────
# 2. Near-duplicate removal (perceptual hashing)
# ─────────────────────────────────────────────────────────────────────────────

def remove_duplicates(class_dir: Path, threshold: int, dry_run: bool) -> list:
    """
    Compute pHash for every image in class_dir.
    If two images have Hamming distance <= threshold, keep the first,
    remove the second.

    Why pHash?
        Unlike MD5 (exact), pHash detects visually identical images that
        differ in format, resolution, or minor compression artefacts.

    Returns list of removed paths.
    """
    hashes = {}          # hash_value -> first_seen_path
    to_remove = []

    imgs = sorted([p for p in class_dir.iterdir()
                   if p.suffix.lower() in VALID_EXTENSIONS])

    for img_path in imgs:
        try:
            with Image.open(img_path) as img:
                h = imagehash.phash(img)
        except Exception:
            continue    # already marked corrupt; skip

        duplicate_of = None
        for existing_hash, existing_path in hashes.items():
            if abs(h - existing_hash) <= threshold:
                duplicate_of = existing_path
                break

        if duplicate_of:
            to_remove.append(img_path)
            if not dry_run:
                img_path.unlink()
        else:
            hashes[h] = img_path

    return to_remove


# ─────────────────────────────────────────────────────────────────────────────
# 3. Main cleaning loop
# ─────────────────────────────────────────────────────────────────────────────

def clean(threshold: int = HASH_THRESHOLD, dry_run: bool = False) -> None:
    class_names = get_class_names()
    SPLITS_DIR.mkdir(parents=True, exist_ok=True)

    manifest_rows = []     # (path, class_name) for cleaned manifest
    stats = {}

    print(f"\n{'Class':<20} {'Total':>7} {'Corrupt':>8} {'Dupes':>8} {'Clean':>7}")
    print("-" * 55)

    for class_name in class_names:
        class_dir = RAW_DIR / class_name
        if not class_dir.exists():
            print(f"  [WARN] {class_name}: folder not found at {class_dir}")
            stats[class_name] = {"total": 0, "corrupt": 0, "dupes": 0, "clean": 0}
            continue

        all_imgs = [p for p in class_dir.iterdir()
                    if p.suffix.lower() in VALID_EXTENSIONS]
        total = len(all_imgs)

        corrupt = remove_corrupt(class_dir, dry_run)
        dupes = remove_duplicates(class_dir, threshold, dry_run)

        remaining = [p for p in class_dir.iterdir()
                     if p.suffix.lower() in VALID_EXTENSIONS]
        clean_count = len(remaining)

        stats[class_name] = {
            "total": total,
            "corrupt": len(corrupt),
            "dupes": len(dupes),
            "clean": clean_count,
        }

        flag = "  [LOW]" if clean_count < MIN_IMAGES_PER_CLASS else ""
        print(f"  {class_name:<18} {total:>7} {len(corrupt):>8} {len(dupes):>8} "
              f"{clean_count:>7}{flag}")

        for img_path in remaining:
            manifest_rows.append({
                "filepath": str(img_path.resolve()),
                "class_name": class_name,
            })

    # ── Write manifest CSV ──────────────────────────────────────────────────
    manifest_path = SPLITS_DIR / "cleaned_manifest.csv"
    if not dry_run:
        with open(manifest_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["filepath", "class_name"])
            writer.writeheader()
            writer.writerows(manifest_rows)
        print(f"\n  Manifest saved: {manifest_path}")
    else:
        print(f"\n  [DRY RUN] Manifest would have {len(manifest_rows)} rows.")

    # ── Low-count warnings ──────────────────────────────────────────────────
    print("\n  --- Low-count classes (< MIN_IMAGES_PER_CLASS={}) ---".format(
        MIN_IMAGES_PER_CLASS))
    any_low = False
    for cls, s in stats.items():
        if s["clean"] < MIN_IMAGES_PER_CLASS:
            any_low = True
            print(f"    {cls}: {s['clean']} images  -> see fallback plan below")
    if not any_low:
        print("    None! All classes meet the minimum.")

    print("\n  FALLBACK OPTIONS for low-count classes:")
    print("  1. Merge into 'other' (simplest, but loses resolution).")
    print("  2. Collect additional phone photos (see scripts/collect_photos.md).")
    print("  3. Web scrape CC0 images (use scripts/scrape_cc0.py – Phase 1 extra).")
    print("  4. Apply heavy augmentation ONLY to the low-count class during training.")

    print(f"\n  Total clean images: {sum(s['clean'] for s in stats.values())}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hash-threshold", type=int, default=HASH_THRESHOLD)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    clean(threshold=args.hash_threshold, dry_run=args.dry_run)
