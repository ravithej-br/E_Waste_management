"""
scripts/download_hf_cfl.py
--------------------------
Downloads a single parquet shard from '4w4kt/waste-dataset-image' on Hugging Face,
filters images of 'light bulbs' (Class label 4), and saves them as JPEGs into:
    data/raw/cfl_bulb/

This gives us the missing cfl_bulb images without having to download the entire 16GB dataset!
"""

import io
from pathlib import Path
from PIL import Image
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "cfl_bulb"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_LABEL_INDEX = 4  # 'light bulbs'
MAX_IMAGES_TO_EXTRACT = 250

def extract_from_shard(shard_filename: str):
    print(f"\n[INFO] Downloading shard {shard_filename} from Hugging Face...")
    file_path = hf_hub_download(
        repo_id="4w4kt/waste-dataset-image",
        filename=shard_filename,
        repo_type="dataset"
    )
    print(f"[OK] Downloaded to: {file_path}")

    print("[INFO] Reading parquet table...")
    table = pq.read_table(file_path, columns=["image", "label"])
    
    extracted = 0
    num_rows = len(table)
    print(f"[INFO] Total rows in shard: {num_rows}")

    labels = table["label"].to_pylist()
    images_col = table["image"]

    for idx, label in enumerate(labels):
        if label == TARGET_LABEL_INDEX:
            img_data = images_col[idx].as_py()
            img_bytes = img_data.get("bytes")
            
            if img_bytes:
                try:
                    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                    save_path = OUTPUT_DIR / f"HF_cfl_bulb_{idx:05d}.jpg"
                    img.save(save_path, "JPEG", quality=92)
                    extracted += 1
                except Exception as err:
                    print(f"  [WARN] Failed to process image {idx}: {err}")
            
            if extracted >= MAX_IMAGES_TO_EXTRACT:
                break

    print(f"\n[SUCCESS] Extracted {extracted} 'light bulbs' images into: {OUTPUT_DIR}")
    return extracted

def main():
    extracted = extract_from_shard("data/test-00000-of-00003.parquet")
    if extracted < 80:
        print(f"[INFO] Only got {extracted} images. Downloading second shard...")
        extracted += extract_from_shard("data/test-00001-of-00003.parquet")

    current_total = len(list(OUTPUT_DIR.glob("*.jpg")))
    print(f"\nFinal count in data/raw/cfl_bulb: {current_total} images.")

if __name__ == "__main__":
    main()
