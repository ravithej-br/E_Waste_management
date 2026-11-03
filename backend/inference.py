"""
backend/inference.py
────────────────────
Memory-only ONNX Runtime Inference Engine.
Processes images strictly in-memory (RAM) via io.BytesIO without disk persistence.
Applies ImageNet preprocessing, temperature scaling (T=0.4923), confidence thresholding,
and attaches India E-Waste 2022 domain guidance and local Bengaluru recycler centers.
"""

import sys
import io
import time
import logging
from pathlib import Path
from typing import Optional
import numpy as np
from PIL import Image
import onnxruntime as ort

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    IMAGE_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD,
    TEMPERATURE,
    DEFAULT_CONFIDENCE_THRESHOLD,
    ONNX_DIR,
    ONNX_INT8_NAME,
    ONNX_FP32_NAME,
)
from src.utils.class_loader import get_class_names
from src.guidance.engine import apply_temperature_scaling, get_guidance
from backend.geo_service import get_nearest_centers

logger = logging.getLogger("inference")


class EwasteInferenceEngine:
    """
    Production ONNX Inference Engine for E-Waste Classification.
    Ensures zero disk storage of uploaded image bytes for complete user privacy.
    """

    def __init__(self, model_path: Optional[Path | str] = None):
        self.class_names = get_class_names()
        self.mean = np.array(IMAGENET_MEAN, dtype=np.float32).reshape(1, 1, 3)
        self.std = np.array(IMAGENET_STD, dtype=np.float32).reshape(1, 1, 3)

        # Select model path: prefer selective INT8, fallback to FP32
        if model_path is None:
            int8_path = ONNX_DIR / ONNX_INT8_NAME
            fp32_path = ONNX_DIR / ONNX_FP32_NAME
            if int8_path.exists():
                self.model_path = int8_path
            elif fp32_path.exists():
                self.model_path = fp32_path
            else:
                raise FileNotFoundError(
                    f"No ONNX model found in {ONNX_DIR}. Expected {ONNX_INT8_NAME} or {ONNX_FP32_NAME}."
                )
        else:
            self.model_path = Path(model_path)

        # Configure ONNX Runtime Session
        session_opts = ort.SessionOptions()
        session_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        session_opts.intra_op_num_threads = 2
        session_opts.log_severity_level = 3  # Error only

        logger.info(f"Loading ONNX model from: {self.model_path.name}")
        self.session = ort.InferenceSession(
            str(self.model_path),
            sess_options=session_opts,
            providers=["CPUExecutionProvider"]
        )

        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

    def preprocess_image(
        self, image_bytes: bytes, center_crop_fraction: float = 1.0
    ) -> tuple[np.ndarray, dict]:
        """
        Preprocesses raw image bytes into normalized CHW float32 batch tensor.
        Zero disk I/O – uses io.BytesIO in memory.

        Args:
            image_bytes:           Raw image file bytes (JPEG/PNG/WebP).
            center_crop_fraction:  0.0–1.0 fraction of the image's shorter side to
                                   center-crop before resize.  1.0 = full frame.
                                   Typical use: 0.65 for real-world wide-table photos.
        """
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            pil_img.verify()  # verify integrity
            # Reopen after verify because verify can corrupt file pointer
            pil_img = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            raise ValueError(f"Corrupt or unreadable image file: {str(e)}")

        orig_w, orig_h = pil_img.size
        orig_format = pil_img.format or "UNKNOWN"

        # Apply EXIF rotation if present (crucial for phone camera orientation)
        from PIL import ImageOps
        pil_img = ImageOps.exif_transpose(pil_img)

        # Convert to RGB
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        w, h = pil_img.size
        ratio = max(w, h) / max(min(w, h), 1)

        # ── Automatic Smart Center-Crop for Real-World Wide Photos ──────────
        # Phone/tablet photos are 16:9 or 4:3 (ratio ≥ 1.4).  When squeezed
        # into 224×224 the entire background (table surface, wall, ceiling
        # glare) occupies most pixels and confuses the classifier.
        # Strategy: crop out 67% central region first, then resize.
        # This mimics the tight studio crops seen in training images.
        effective_crop = center_crop_fraction  # caller can override
        if effective_crop < 1.0 and (w > 1 and h > 1):
            # Centre-crop to `effective_crop` fraction of the image
            crop_w = int(w * effective_crop)
            crop_h = int(h * effective_crop)
            left   = (w - crop_w) // 2
            top    = (h - crop_h) // 2
            pil_img = pil_img.crop((left, top, left + crop_w, top + crop_h))
            w, h = pil_img.size
            ratio = max(w, h) / max(min(w, h), 1)

        # ── Resize Strategy ─────────────────────────────────────────────────
        # For still-wide images (ratio > 1.3) use centre-fit to maintain
        # aspect ratio; for near-square images use direct resize.
        if ratio > 1.3:
            img_resized = ImageOps.fit(pil_img, (IMAGE_SIZE, IMAGE_SIZE), Image.Resampling.BILINEAR)
        else:
            img_resized = pil_img.resize((IMAGE_SIZE, IMAGE_SIZE), Image.Resampling.BILINEAR)

        # Convert to numpy float32 normalized to [0, 1]
        arr = np.array(img_resized, dtype=np.float32) / 255.0

        # Normalize with ImageNet mean and std
        arr = (arr - self.mean) / self.std

        # Transpose from HWC (224, 224, 3) to CHW (3, 224, 224)
        arr = arr.transpose(2, 0, 1)

        # Expand batch dimension (1, 3, 224, 224)
        tensor = np.expand_dims(arr, axis=0).astype(np.float32)

        meta = {
            "original_width": orig_w,
            "original_height": orig_h,
            "format": orig_format,
        }
        return tensor, meta

    def predict(
        self,
        image_bytes: bytes,
        threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        center_crop_fraction: float = 1.0,
    ) -> dict:
        """
        Executes end-to-end in-memory classification, calibration, guidance lookup,
        and geographic recycler proximity matching.

        Args:
            center_crop_fraction: 0.0–1.0.  1.0 = full frame (default).
                                  Pass 0.65 for real-world wide-table photos to
                                  auto-crop background before classification.
        """
        t0 = time.perf_counter()

        # 1. Preprocessing (with optional smart center-crop)
        tensor, meta = self.preprocess_image(image_bytes, center_crop_fraction=center_crop_fraction)
        t1 = time.perf_counter()

        # 2. ONNX Forward Pass
        outputs = self.session.run([self.output_name], {self.input_name: tensor})
        raw_logits = outputs[0]  # shape (1, 7)
        t2 = time.perf_counter()

        # 3. Calibrated Softmax via Temperature Scaling (T = 0.4923)
        calibrated_probs = apply_temperature_scaling(raw_logits, temperature=TEMPERATURE)[0]

        # 4. Top-1 and Top-3 Rankings
        top_idx = int(np.argmax(calibrated_probs))
        top_conf = float(calibrated_probs[top_idx])
        top_label = self.class_names[top_idx]

        sorted_indices = np.argsort(calibrated_probs)[::-1][:3]
        top_3 = [
            {"label": self.class_names[i], "confidence": round(float(calibrated_probs[i]), 4)}
            for i in sorted_indices
        ]

        # 5. Regulatory Guidance Engine
        guidance = get_guidance(
            prediction_index_or_name=top_label,
            confidence=top_conf,
            threshold=threshold,
            top_3_predictions=top_3
        )

        # 6. Proximity Recycling Facilities
        nearest_centers = get_nearest_centers(
            user_lat=user_lat,
            user_lon=user_lon,
            class_name=top_label,
            limit=3
        )

        t3 = time.perf_counter()

        preprocess_ms = round((t1 - t0) * 1000, 2)
        inference_ms = round((t2 - t1) * 1000, 2)
        total_ms = round((t3 - t0) * 1000, 2)

        return {
            "prediction": top_label,
            "class_index": top_idx,
            "calibrated_confidence": round(top_conf, 4),
            "threshold": round(float(threshold), 4),
            "is_confident": bool(top_conf >= threshold),
            "top_3": top_3,
            "guidance": guidance,
            "nearest_recyclers": nearest_centers,
            "image_metadata": meta,
            "latency_ms": {
                "preprocess": preprocess_ms,
                "inference": inference_ms,
                "total": total_ms
            },
            "model_info": {
                "name": self.model_path.name,
                "temperature": TEMPERATURE,
                "execution_provider": "CPUExecutionProvider"
            }
        }


# Global singleton instance for FastAPI reuse
_GLOBAL_ENGINE: Optional[EwasteInferenceEngine] = None


def get_inference_engine() -> EwasteInferenceEngine:
    """Returns singleton inference engine instance."""
    global _GLOBAL_ENGINE
    if _GLOBAL_ENGINE is None:
        _GLOBAL_ENGINE = EwasteInferenceEngine()
    return _GLOBAL_ENGINE
