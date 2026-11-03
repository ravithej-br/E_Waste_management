"""
tests/test_frontend.py
──────────────────────
Unit tests verifying frontend dependencies, sample loading, and data integrity.
"""

import sys
import io
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.inference import get_inference_engine
from backend.geo_service import load_recyclers_db, get_nearest_centers


def test_frontend_engine_prediction():
    """Verify inference engine works with synthetic image and produces expected frontend keys."""
    engine = get_inference_engine()
    img = Image.new("RGB", (224, 224), color=(200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")

    res = engine.predict(buf.getvalue(), threshold=0.65, user_lat=12.9716, user_lon=77.5946)
    assert "prediction" in res
    assert "calibrated_confidence" in res
    assert "top_3" in res
    assert "guidance" in res
    assert "nearest_recyclers" in res
    assert len(res["nearest_recyclers"]) > 0


def test_recyclers_database_loading():
    """Verify Bengaluru recyclers database loads properly for frontend display."""
    db = load_recyclers_db()
    centers = db.get("centers", [])
    assert len(centers) >= 8
    for c in centers:
        assert "name" in c
        assert "coordinates" in c
        assert "lat" in c["coordinates"]
        assert "lon" in c["coordinates"]
        assert "phone" in c
        assert "kspcb_auth_no" in c
        # Verify enriched fields are present
        assert "opening_hours" in c
        assert "disposal_instructions" in c


def test_nearest_centers_distance_sorting():
    """Verify proximity ranking calculation for frontend maps."""
    ranked = get_nearest_centers(user_lat=12.9716, user_lon=77.5946, limit=5)
    assert len(ranked) == 5
    for i in range(len(ranked) - 1):
        assert ranked[i]["distance_km"] <= ranked[i + 1]["distance_km"]
