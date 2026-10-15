"""
scripts/download_and_inspect.py
--------------------------------
Downloads both confirmed Kaggle datasets and prints:
  - All folder (class) names found
  - Image count per folder
  - Sample file names

Run this ONCE to discover real class names.
Then we update CLASS_MAPPING in src/dataset/ingest.py.

Usage:
    pip install kagglehub
    python scripts/download_and_inspect.py

Requires:
    - Kaggle API key at C:/Users/<you>/.kaggle/kaggle.json
      OR set env vars KAGGLE_USERNAME and KAGGLE_KEY
"""

import os
import sys
from pathlib import Path
from collections import defaultdict

# ── Try to import kagglehub ──────────────────────────────────────────────────
try:
    import kagglehub
except ImportError:
    print("[ERROR] kagglehub not installed.")
    print("  Run:  pip install kagglehub")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOWNLOAD_CACHE = PROJECT_ROOT / "data" / "raw" / "downloads"
DOWNLOAD_CACHE.mkdir(parents=True, exist_ok=True)

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

DATASETS = [
    {
        "id":     "DS1",
        "slug":   "akshat103/e-waste-image-dataset",
        "name":   "E-Waste Image Dataset",
    },
    {
        "id":     "DS4",
        "slug":   "aryaminus/electronic-components",
        "name":   "Electronic Components",
    },
]


def count_images(folder: Path) -> dict:
    """Return {subfolder_name: image_count} for all direct subfolders."""
    result = {}
    for sub in sorted(folder.iterdir()):
        if sub.is_dir():
            imgs = [f for f in sub.rglob("*")
                    if f.suffix.lower() in VALID_EXTENSIONS]
            result[sub.name] = len(imgs)
    return result


def inspect_path(path: Path, dataset_id: str, dataset_name: str):
    print(f"\n{'='*60}")
    print(f"  {dataset_id}: {dataset_name}")
    print(f"  Downloaded to: {path}")
    print(f"{'='*60}")

    if not path.exists():
        print("  [ERROR] Path does not exist!")
        return

    # Find all image-containing directories
    all_dirs = [d for d in path.rglob("*") if d.is_dir()]

    # Find directories that directly contain images
    class_dirs = {}
    for d in all_dirs:
        imgs = [f for f in d.iterdir()
                if f.is_file() and f.suffix.lower() in VALID_EXTENSIONS]
        if imgs:
            class_dirs[d.name] = (len(imgs), d, imgs[0].name)

    if not class_dirs:
        print("  [WARN] No image-containing subdirectories found.")
        print("  Directory tree:")
        for d in sorted(all_dirs)[:20]:
            rel = d.relative_to(path)
            print(f"    {rel}")
        return

    print(f"\n  Found {len(class_dirs)} class folder(s):\n")
    print(f"  {'Folder Name':<30} {'Images':>8}  {'Sample file'}")
    print(f"  {'-'*30} {'-'*8}  {'-'*25}")

    total = 0
    for name, (count, folder_path, sample) in sorted(class_dirs.items(),
                                                       key=lambda x: -x[1][0]):
        print(f"  {name:<30} {count:>8}  {sample}")
        total += count

    print(f"\n  TOTAL IMAGES: {total}")
    print(f"\n  COPY THESE FOLDER NAMES into CLASS_MAPPING in src/dataset/ingest.py")


def main():
    downloaded_paths = {}

    for ds in DATASETS:
        print(f"\n[Downloading] {ds['name']} ({ds['slug']}) ...")
        try:
            path = kagglehub.dataset_download(ds["slug"])
            downloaded_paths[ds["id"]] = Path(path)
            print(f"  [OK] Downloaded to: {path}")
        except Exception as e:
            print(f"  [FAIL] Could not download {ds['slug']}")
            print(f"         Error: {e}")
            print(f"         Check your Kaggle API key and internet connection.")
            downloaded_paths[ds["id"]] = None

    # Inspect each downloaded dataset
    for ds in DATASETS:
        path = downloaded_paths.get(ds["id"])
        if path:
            inspect_path(path, ds["id"], ds["name"])
        else:
            print(f"\n  [SKIP] {ds['id']}: download failed.")

    print("\n" + "="*60)
    print("  NEXT STEP:")
    print("  Paste the folder names above as a message and")
    print("  the CLASS_MAPPING in src/dataset/ingest.py will be updated.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
