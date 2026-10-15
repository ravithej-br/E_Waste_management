"""
tests/test_api.py
─────────────────
Comprehensive integration and unit test suite for FastAPI backend endpoints.
Uses starlette.testclient.TestClient for synchronous in-memory HTTP testing.
"""

import sys
import io
from pathlib import Path
import pytest
from PIL import Image
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.main import app

client = TestClient(app)


def create_test_image(format="JPEG", size=(224, 224), color=(100, 150, 200)) -> bytes:
    """Helper to generate in-memory synthetic image bytes."""
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()


# ─────────────────────────────────────────────
# ENDPOINT TESTS
# ─────────────────────────────────────────────

def test_root_endpoint():
    """Verify root metadata endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["version"] == "1.0.0"
    assert "/predict" in data["endpoints"]["predict"]


def test_health_endpoint():
    """Verify health endpoint reports ok and loads 7 classes."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["classes_count"] == 7
    assert "onnx" in data["model_loaded"]


def test_classes_endpoint():
    """Verify all 7 classes are returned with hazard descriptions."""
    response = client.get("/classes")
    assert response.status_code == 200
    data = response.json()
    assert data["num_classes"] == 7
    labels = [c["label"] for c in data["classes"]]
    assert "battery" in labels
    assert "cfl_bulb" in labels
    assert "keyboard" in labels
    assert "mobile_phone" in labels
    assert "monitor_crt" in labels
    assert "pcb" in labels
    assert "other" in labels


def test_recyclers_endpoint_default():
    """Verify Bengaluru recyclers endpoint with default coordinates."""
    response = client.get("/recyclers")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] > 0
    assert len(data["centers"]) <= 5
    # Check distance ordering
    distances = [c["distance_km"] for c in data["centers"]]
    assert distances == sorted(distances)


def test_recyclers_endpoint_filter_category():
    """Verify filtering recyclers by accepted material class."""
    response = client.get("/recyclers?class_name=battery&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] <= 3
    for center in data["centers"]:
        assert "battery" in center["categories_accepted"]


def test_predict_valid_image():
    """Verify end-to-end prediction with in-memory valid image."""
    img_bytes = create_test_image(format="JPEG")
    files = {"file": ("test_sample.jpg", img_bytes, "image/jpeg")}
    response = client.post("/predict", files=files)
    assert response.status_code == 200
    data = response.json()

    assert "prediction" in data
    assert "calibrated_confidence" in data
    assert "top_3" in data
    assert len(data["top_3"]) == 3
    assert "guidance" in data
    assert "nearest_recyclers" in data
    assert "latency_ms" in data
    assert "preprocess" in data["latency_ms"]
    assert "inference" in data["latency_ms"]


def test_predict_png_format():
    """Verify prediction accepts PNG format."""
    img_bytes = create_test_image(format="PNG")
    files = {"file": ("sample.png", img_bytes, "image/png")}
    response = client.post("/predict", files=files)
    assert response.status_code == 200


def test_predict_unsupported_extension():
    """Verify rejection of non-image file extensions with 415."""
    files = {"file": ("document.txt", b"plain text content", "text/plain")}
    response = client.post("/predict", files=files)
    assert response.status_code == 415
    assert "Unsupported file extension" in response.json()["detail"]


def test_predict_empty_file():
    """Verify rejection of empty file uploads with 400."""
    files = {"file": ("empty.jpg", b"", "image/jpeg")}
    response = client.post("/predict", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_predict_corrupt_file():
    """Verify rejection of corrupt image bytes with 400."""
    corrupt_bytes = b"\xFF\xD8\xFF\xE0" + b"CORRUPTDATA12345"
    files = {"file": ("corrupt.jpg", corrupt_bytes, "image/jpeg")}
    response = client.post("/predict", files=files)
    assert response.status_code == 400
    assert "corrupt" in response.json()["detail"].lower()


def test_zero_disk_leak():
    """Verify that prediction leaves zero leftover files on disk."""
    import tempfile
    before_files = set(Path(tempfile.gettempdir()).glob("*"))

    img_bytes = create_test_image()
    files = {"file": ("leak_test.jpg", img_bytes, "image/jpeg")}
    response = client.post("/predict", files=files)
    assert response.status_code == 200

    after_files = set(Path(tempfile.gettempdir()).glob("*"))
    # No e-waste uploads should be dumped into temp
    new_files = [f.name for f in (after_files - before_files) if "leak_test" in f.name]
    assert len(new_files) == 0
