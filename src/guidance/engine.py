"""
src/guidance/engine.py
──────────────────────
Guidance Engine implementing domain logic, confidence safeguards, and
India E-Waste (Management) Rules 2022 knowledge base lookup.

Key features:
  - Label consistency enforced via classes.json.
  - Temperature scaling applied using calibrated parameter T = 0.4923.
  - Safeguard threshold (0.65): Intercepts low-confidence or ambiguous photos,
    returning structured retake advice rather than dangerous false guidance.
  - Returns complete hazard profile, chemical toxins, safe handling, legal disposal,
    and mandatory informational disclaimer.
"""

import sys
import json
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    CLASSES_JSON,
    TEMPERATURE,
    DEFAULT_CONFIDENCE_THRESHOLD,
)
from src.utils.class_loader import get_class_names, get_index_to_label

KB_PATH = Path(__file__).resolve().parent / "knowledge_base.json"


def load_knowledge_base() -> dict:
    if not KB_PATH.exists():
        raise FileNotFoundError(f"Knowledge base not found at: {KB_PATH}")
    with open(KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# Preload Knowledge Base
_KB = load_knowledge_base()
_KB_DISCLAIMER = _KB.get(
    "_disclaimer",
    "This guidance is informational and educational. It does not constitute formal legal or certified safety advice."
)


def apply_temperature_scaling(logits: np.ndarray, temperature: float = TEMPERATURE) -> np.ndarray:
    """
    Applies temperature scaling to raw model logits and returns calibrated probabilities.
    Formula: p_i = exp(z_i / T) / sum(exp(z_j / T))
    """
    if temperature <= 0:
        raise ValueError("Temperature parameter must be positive.")
    
    scaled_logits = logits / temperature
    # Numerical stability shift
    exp_logits = np.exp(scaled_logits - np.max(scaled_logits, axis=-1, keepdims=True))
    probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
    return probs


def get_guidance(
    prediction_index_or_name: int | str,
    confidence: float,
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    top_3_predictions: list[dict] | None = None
) -> dict:
    """
    Retrieves complete hazard and disposal guidance for a prediction.
    Applies confidence safeguard thresholding.

    Args:
        prediction_index_or_name: class label (str) or index (int)
        confidence: calibrated top-1 confidence probability (0.0 to 1.0)
        threshold: safeguard cutoff (default 0.65 from Phase 3 calibration)
        top_3_predictions: optional list of [{'label': str, 'confidence': float}, ...]
    """
    class_names = get_class_names()

    if isinstance(prediction_index_or_name, int):
        if not (0 <= prediction_index_or_name < len(class_names)):
            raise IndexError(f"Class index {prediction_index_or_name} out of range (0-{len(class_names)-1}).")
        class_name = class_names[prediction_index_or_name]
    else:
        class_name = str(prediction_index_or_name).lower().strip()
        if class_name not in class_names:
            class_name = "other"

    # ── Safeguard: Confidence Threshold Interception ─────────────────────────
    if confidence < threshold:
        return {
            "status": "uncertain",
            "message": "Confidence is below the safety threshold. The image may be blurry, poorly lit, or ambiguous.",
            "predicted_class": class_name,
            "calibrated_confidence": round(float(confidence), 4),
            "confidence_threshold": round(float(threshold), 4),
            "top_3": top_3_predictions or [],
            "retake_tips": [
                "Ensure the electronic item is well-lit and not in shadow.",
                "Frame the item closer so it fills at least 60% of the camera view.",
                "Place the item on a plain, uncluttered background.",
                "Avoid harsh flash reflections on glossy screens or casings."
            ],
            "disclaimer": _KB_DISCLAIMER
        }

    # ── Full Authoritative Guidance ──────────────────────────────────────────
    kb_data = _KB["classes"].get(class_name, _KB["classes"]["other"])

    return {
        "status": "success",
        "class_name": class_name,
        "display_name": kb_data.get("display_name", class_name.title()),
        "confidence": round(float(confidence), 4),
        "confidence_threshold": round(float(threshold), 4),
        "top_3": top_3_predictions or [],
        "hazard_level": kb_data.get("hazard_level", "UNKNOWN"),
        "toxic_compounds": kb_data.get("toxic_compounds", []),
        "safe_handling": kb_data.get("safe_handling", []),
        "storage_tips": kb_data.get("storage_tips", []),
        "disposal_method": kb_data.get("disposal_method", ""),
        "extra_care_notes": kb_data.get("extra_care_notes", ""),
        "source_reference": kb_data.get("source_reference", ""),
        "last_checked": kb_data.get("last_checked", ""),
        "verify": kb_data.get("verify", False),
        "disclaimer": _KB_DISCLAIMER
    }


def demo_engine():
    print(f"\n{'='*70}")
    print("  GUIDANCE ENGINE VERIFICATION DEMO")
    print(f"  Knowledge Base Version: {_KB.get('_version')} | Calibrated Temp: {TEMPERATURE}")
    print(f"  Safeguard Threshold:    {DEFAULT_CONFIDENCE_THRESHOLD}")
    print(f"{'='*70}\n")

    # Test 1: High confidence battery
    print("--- Test 1: High-Confidence Battery (94%) ---")
    res1 = get_guidance("battery", confidence=0.94)
    print(f"  Status:       {res1['status']}")
    print(f"  Item:         {res1['display_name']}")
    print(f"  Hazard Level: {res1['hazard_level']}")
    print(f"  Disposal:     {res1['disposal_method'][:80]}...")
    print(f"  Extra Care:   {res1['extra_care_notes'][:80]}...")

    # Test 2: Low confidence image (triggered safeguard)
    print("\n--- Test 2: Low-Confidence Image (52% < 65% threshold) ---")
    res2 = get_guidance("pcb", confidence=0.52)
    print(f"  Status:       {res2['status']}")
    print(f"  Message:      {res2['message']}")
    print(f"  Retake Tips:  {res2['retake_tips'][0]}")

    # Test 3: High-hazard CFL bulb
    print("\n--- Test 3: CFL Bulb (Mercury Protocol) ---")
    res3 = get_guidance("cfl_bulb", confidence=0.91)
    print(f"  Status:       {res3['status']}")
    print(f"  Toxins:       {res3['toxic_compounds'][0]}")
    print(f"  Extra Care:   {res3['extra_care_notes'][:90]}...")
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    demo_engine()
