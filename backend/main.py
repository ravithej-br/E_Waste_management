"""
backend/main.py
───────────────
FastAPI application for the Lightweight E-Waste Classification and Recycling Guidance System.

Endpoints:
  - GET  /         : Service metadata and documentation links
  - GET  /health   : Health check, model status, and runtime info
  - POST /predict  : In-memory image classification, temperature scaling, legal guidance, nearest recyclers
  - GET  /recyclers: Query Bengaluru KSPCB authorized recyclers with GPS proximity ranking
  - GET  /classes  : Supported classes and hazard designations
"""

import sys
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Query, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    CORS_ORIGINS,
    MAX_UPLOAD_SIZE_MB,
    ALLOWED_EXTENSIONS,
    RATE_LIMIT_PER_MIN,
    DEFAULT_CONFIDENCE_THRESHOLD,
)
from src.utils.class_loader import get_class_names
from backend.inference import get_inference_engine
from backend.geo_service import get_nearest_centers, load_recyclers_db

# ─────────────────────────────────────────────
# RATE LIMITING & APP INITIALIZATION
# ─────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{RATE_LIMIT_PER_MIN}/minute"])

app = FastAPI(
    title="Lightweight E-Waste Classification & Recycling Guidance API",
    description=(
        "Production-grade, privacy-first REST API for real-time e-waste classification, "
        "calibrated hazard assessment (India E-Waste Rules 2022), and Bengaluru recycling facility locator."
    ),
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─────────────────────────────────────────────
# CORS MIDDLEWARE
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()


# ─────────────────────────────────────────────
# REQUEST TIMING MIDDLEWARE
# ─────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    response.headers["X-Process-Time-Ms"] = f"{duration * 1000:.2f}"
    return response


# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/", tags=["Info"])
async def root():
    """Root metadata endpoint."""
    return {
        "service": "E-Waste Classification and Recycling Guidance System",
        "version": "1.0.0",
        "team": "CSE Mini-Project, Bengaluru, Karnataka",
        "docs_url": "/docs",
        "endpoints": {
            "health": "/health",
            "predict": "/predict (POST multipart/form-data)",
            "recyclers": "/recyclers",
            "classes": "/classes",
        },
        "privacy": "Zero disk persistence – images are processed in-memory only and discarded immediately."
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint confirming engine readiness and uptime."""
    engine = get_inference_engine()
    uptime_seconds = round(time.time() - START_TIME, 1)

    return {
        "status": "ok",
        "uptime_seconds": uptime_seconds,
        "model_loaded": engine.model_path.name,
        "classes_count": len(engine.class_names),
        "execution_provider": "CPUExecutionProvider",
    }


@app.get("/classes", tags=["Classes"])
async def list_classes():
    """Returns list of supported e-waste classes and hazard status."""
    class_names = get_class_names()
    hazard_map = {
        "battery": "CRITICAL HAZARD (Lithium/Lead thermal runaway, corrosive electrolyte)",
        "cfl_bulb": "HIGH HAZARD (Toxic mercury vapor, phosphors)",
        "monitor_crt": "HIGH HAZARD (Lead oxide implosion hazard, barium)",
        "pcb": "MODERATE-HIGH HAZARD (Brominated flame retardants, solder lead)",
        "mobile_phone": "MODERATE HAZARD (Contains lithium battery, tantalum, gold)",
        "keyboard": "LOW HAZARD (Thermoplastics, flame retardants, non-hazardous electronic)",
        "other": "UNKNOWN HAZARD (General or unclassified e-waste)",
    }
    return {
        "num_classes": len(class_names),
        "classes": [
            {
                "index": idx,
                "label": name,
                "hazard_level": hazard_map.get(name, "UNKNOWN")
            }
            for idx, name in enumerate(class_names)
        ]
    }


@app.get("/recyclers", tags=["Recyclers"])
async def list_recyclers(
    class_name: Optional[str] = Query(None, description="Filter by accepted e-waste class"),
    user_lat: Optional[float] = Query(None, description="User latitude (default: Central Bengaluru 12.9716)"),
    user_lon: Optional[float] = Query(None, description="User longitude (default: Central Bengaluru 77.5946)"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of centers to return")
):
    """
    Returns verified Bengaluru e-waste recycling facilities ranked by proximity.
    """
    centers = get_nearest_centers(
        user_lat=user_lat,
        user_lon=user_lon,
        class_name=class_name,
        limit=limit
    )
    return {
        "count": len(centers),
        "user_coordinates": {
            "lat": user_lat or 12.9716,
            "lon": user_lon or 77.5946,
            "is_default": user_lat is None or user_lon is None
        },
        "filter_class": class_name,
        "centers": centers
    }


@app.post("/predict", tags=["Inference"])
@limiter.limit(f"{RATE_LIMIT_PER_MIN}/minute")
async def predict(
    request: Request,
    file: UploadFile = File(..., description="E-waste image file (JPG, PNG, WebP <= 10MB)"),
    threshold: float = Query(
        DEFAULT_CONFIDENCE_THRESHOLD,
        ge=0.0,
        le=1.0,
        description="Confidence safeguard cutoff (default 0.65)"
    ),
    user_lat: Optional[float] = Query(None, description="User GPS latitude for recycler ranking"),
    user_lon: Optional[float] = Query(None, description="User GPS longitude for recycler ranking"),
):
    """
    Classify uploaded e-waste image.
    Enforces in-memory processing, file size limits, temperature scaling,
    safeguard thresholding, regulatory guidance, and nearest recycler lookup.
    """
    # 1. Extension validation
    filename = file.filename or "upload.jpg"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file extension '{ext}'. Allowed extensions: {list(ALLOWED_EXTENSIONS)}"
        )

    # 2. In-memory read and size validation
    max_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    image_bytes = await file.read()

    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    if len(image_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({round(len(image_bytes) / (1024 * 1024), 2)} MB) exceeds {MAX_UPLOAD_SIZE_MB} MB limit."
        )

    # 3. Predict via Inference Engine
    try:
        engine = get_inference_engine()
        result = engine.predict(
            image_bytes=image_bytes,
            threshold=threshold,
            user_lat=user_lat,
            user_lon=user_lon,
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or corrupt image: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failure: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
