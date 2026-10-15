"""
tests/test_guidance.py
──────────────────────
Unit tests for the Guidance Engine and Knowledge Base integrity.
"""

import pytest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import DEFAULT_CONFIDENCE_THRESHOLD, TEMPERATURE
from src.utils.class_loader import get_class_names
from src.guidance.engine import get_guidance, load_knowledge_base, apply_temperature_scaling
import numpy as np


def test_knowledge_base_covers_all_classes():
    """Verify that every class in classes.json exists in knowledge_base.json."""
    classes = get_class_names()
    kb = load_knowledge_base()
    kb_classes = kb["classes"]

    for cls in classes:
        assert cls in kb_classes, f"Class '{cls}' from classes.json missing in knowledge_base.json!"
        item = kb_classes[cls]
        assert "hazard_level" in item
        assert "toxic_compounds" in item
        assert "safe_handling" in item
        assert "disposal_method" in item
        assert len(item["safe_handling"]) > 0


def test_confidence_safeguard_triggers_on_low_confidence():
    """Verify that confidence below threshold returns 'uncertain' status with retake tips."""
    low_conf = DEFAULT_CONFIDENCE_THRESHOLD - 0.10
    result = get_guidance("battery", confidence=low_conf)

    assert result["status"] == "uncertain"
    assert "retake_tips" in result
    assert len(result["retake_tips"]) >= 3
    assert "disclaimer" in result


def test_high_confidence_returns_full_guidance():
    """Verify that confidence >= threshold returns 'success' and full safety protocol."""
    high_conf = DEFAULT_CONFIDENCE_THRESHOLD + 0.15
    result = get_guidance("battery", confidence=high_conf)

    assert result["status"] == "success"
    assert result["hazard_level"] == "HIGH"
    assert len(result["toxic_compounds"]) > 0
    assert "extra_care_notes" in result
    assert "disclaimer" in result


def test_extra_care_notes_for_hazardous_items():
    """Verify special hazard notes for lithium batteries, CRT monitors, and CFL bulbs."""
    for hazardous_class in ["battery", "cfl_bulb", "monitor_crt"]:
        res = get_guidance(hazardous_class, confidence=0.95)
        assert res["status"] == "success"
        assert len(res["extra_care_notes"]) > 20, f"Missing detailed extra care note for {hazardous_class}"


def test_temperature_scaling_output_validity():
    """Verify temperature scaling yields a valid probability distribution summing to 1."""
    logits = np.array([2.5, -1.0, 0.5, 3.2, -0.2, 1.1, 0.0])
    probs = apply_temperature_scaling(logits, temperature=TEMPERATURE)

    assert np.isclose(np.sum(probs), 1.0, atol=1e-5)
    assert np.all(probs >= 0.0)
    assert np.all(probs <= 1.0)
