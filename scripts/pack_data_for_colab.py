"""
scripts/pack_data_for_colab.py
──────────────────────────────
Zips data/processed/ (train, val, test) into data/processed_data.zip (~68 MB).
Member B can upload this zip file directly to Google Drive or Google Colab for training.
"""

import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_ZIP = PROJECT_ROOT / "data" / "processed_data.zip"

def pack_dataset():
    if not PROCESSED_DIR.exists():
        print(f"[ERROR] Processed data directory not found: {PROCESSED_DIR}")
        return

    print(f"[INFO] Compressing {PROCESSED_DIR} into {OUTPUT_ZIP} ...")
    count = 0
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in PROCESSED_DIR.rglob("*"):
            if f.is_file():
                rel_path = f.relative_to(PROCESSED_DIR.parent)
                zf.write(f, arcname=str(rel_path))
                count += 1

    size_mb = OUTPUT_ZIP.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] Packaged {count} files into {OUTPUT_ZIP} ({size_mb:.2f} MB).")
    print("\nHow to use in Google Colab:")
    print("  1. Upload processed_data.zip to your Google Drive or Colab /content/")
    print("  2. In Colab run: !unzip -q /content/drive/MyDrive/processed_data.zip -d ./data/")

if __name__ == "__main__":
    pack_dataset()
