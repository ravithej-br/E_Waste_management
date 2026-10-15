"""
config.py  –  Single source of truth for all hyperparameters and paths.
Every other module imports from here. Never hardcode magic numbers elsewhere.
"""

import os
from pathlib import Path

# ─────────────────────────────────────────────
# ROOT PATHS (relative to project root)
# ─────────────────────────────────────────────
PROJECT_ROOT   = Path(__file__).resolve().parent
DATA_DIR       = PROJECT_ROOT / "data"
RAW_DIR        = DATA_DIR / "raw"
PROCESSED_DIR  = DATA_DIR / "processed"
SPLITS_DIR     = DATA_DIR / "splits"
REAL_WORLD_DIR = DATA_DIR / "real_world_test"

MODELS_DIR       = PROJECT_ROOT / "models"
CHECKPOINTS_DIR  = MODELS_DIR / "checkpoints"
ONNX_DIR         = MODELS_DIR / "onnx"

CLASSES_JSON = PROJECT_ROOT / "classes.json"

# ─────────────────────────────────────────────
# IMAGE SETTINGS
# ─────────────────────────────────────────────
IMAGE_SIZE   = 224          # EfficientNet-B0 and MobileNetV3-Small input
NUM_CHANNELS = 3
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD  = (0.229, 0.224, 0.225)

# ─────────────────────────────────────────────
# DATASET SPLIT SETTINGS
# ─────────────────────────────────────────────
TRAIN_RATIO = 0.70
VAL_RATIO   = 0.15
TEST_RATIO  = 0.15
RANDOM_SEED = 42           # fixed for reproducibility – never change after splitting
MIN_IMAGES_PER_CLASS = 80  # below this, trigger fallback plan (see Phase 1)
HASH_THRESHOLD = 8         # perceptual hash distance for near-duplicate detection

# ─────────────────────────────────────────────
# TRAINING SETTINGS
# ─────────────────────────────────────────────
BATCH_SIZE        = 32
NUM_WORKERS       = 2      # set to 0 on Windows if DataLoader hangs
PIN_MEMORY        = True   # set to False if running on CPU only

# Stage 1 – frozen backbone
STAGE1_LR      = 1e-3
STAGE1_EPOCHS  = 5

# Stage 2 – fine-tune last blocks
STAGE2_LR      = 1e-4
STAGE2_EPOCHS  = 10

WEIGHT_DECAY       = 1e-4
LABEL_SMOOTHING    = 0.1   # range 0.0-0.2; 0.1 is a good starting point
EARLY_STOP_PATIENCE = 5    # stop if val loss doesn't improve for 5 epochs
GRAD_CLIP_NORM      = 1.0  # gradient clipping max norm

# Mixed precision
USE_AMP = True             # torch.cuda.amp; set False on CPU

# ─────────────────────────────────────────────
# EFFICIENTNET-B0 MODEL SETTINGS
# ─────────────────────────────────────────────
EFFICIENTNET_MODEL_NAME = "efficientnet_b0"  # timm model name
MOBILENET_MODEL_NAME    = "mobilenetv3_small_100"  # timm model name

# ─────────────────────────────────────────────
# CONFIDENCE / THRESHOLD SETTINGS (Calibrated in Phase 3)
# ─────────────────────────────────────────────
# Empirically chosen from validation coverage-vs-accuracy curve:
DEFAULT_CONFIDENCE_THRESHOLD = 0.65
# Calibrated Temperature scaling parameter (minimizes NLL on validation logits):
TEMPERATURE = 0.4923


# ─────────────────────────────────────────────
# ONNX / QUANTIZATION SETTINGS
# ─────────────────────────────────────────────
ONNX_OPSET         = 17
ONNX_FP32_NAME     = "efficientnet_b0_fp32.onnx"
ONNX_INT8_NAME     = "efficientnet_b0_int8.onnx"
ONNX_FP32_MOBILE   = "mobilenetv3_small_fp32.onnx"
CALIBRATION_SAMPLES = 200  # images from train split used for INT8 calibration

# ─────────────────────────────────────────────
# BACKEND SETTINGS
# ─────────────────────────────────────────────
MAX_UPLOAD_SIZE_MB  = 10
ALLOWED_EXTENSIONS  = {".jpg", ".jpeg", ".png", ".webp"}
CORS_ORIGINS        = ["*"]  # tighten before production
RATE_LIMIT_PER_MIN  = 30
NOMINATIM_USER_AGENT = "ewaste-classifier/1.0 (your-email@example.com)"  # FILL IN
NOMINATIM_TIMEOUT    = 5     # seconds
NOMINATIM_CACHE_TTL  = 3600  # seconds (1 hour)

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────
LOG_LEVEL = "INFO"
METRICS_LOG_DIR = PROJECT_ROOT / "logs"
