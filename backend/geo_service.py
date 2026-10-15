"""
backend/geo_service.py
──────────────────────
Geographic Recycler Lookup Service for Bengaluru, Karnataka, India.

Combines:
  1. OpenStreetMap (OSM) Nominatim API with strict rate-limiting & caching.
  2. Authoritative Bengaluru Recycler Fallback Database (KSPCB & CPCB verified).
  3. Proximity ranking via Haversine great-circle distance.
  4. Material-specific filtering (only returns centers accepting the detected class).
"""

import sys
import time
import math
import json
import logging
from pathlib import Path
import httpx

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    NOMINATIM_USER_AGENT,
    NOMINATIM_TIMEOUT,
    NOMINATIM_CACHE_TTL,
)

logger = logging.getLogger("geo_service")

RECYCLERS_DB_PATH = Path(__file__).resolve().parent / "bengaluru_recyclers.json"

# In-memory TTL cache for external Nominatim responses: {query_key: (timestamp, data)}
_NOMINATIM_CACHE: dict[str, tuple[float, list]] = {}
_LAST_REQUEST_TIMESTAMP = 0.0

# Default Central Bengaluru coordinates (Majestic / Vidhana Soudha)
DEFAULT_BLR_LAT = 12.9716
DEFAULT_BLR_LON = 77.5946


def load_recyclers_db() -> list[dict]:
    """Loads curated Bengaluru recycling facilities."""
    if not RECYCLERS_DB_PATH.exists():
        logger.warning(f"Recyclers database not found at {RECYCLERS_DB_PATH}")
        return []
    with open(RECYCLERS_DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("centers", [])


_CENTERS = load_recyclers_db()


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance in kilometers between two GPS coordinates
    using the Haversine formula.
    """
    R = 6371.0  # Earth radius in kilometers

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


async def query_nominatim(lat: float, lon: float, category: str = "e-waste") -> list[dict]:
    """
    Queries OpenStreetMap Nominatim API for recycling facilities.
    Enforces Nominatim Usage Policy:
      - Custom identifiable User-Agent
      - Max 1 request per second
      - 5-second timeout
      - 1-hour cache
    """
    global _LAST_REQUEST_TIMESTAMP
    cache_key = f"{round(lat, 2)}_{round(lon, 2)}_{category}"
    now = time.time()

    # Check Cache
    if cache_key in _NOMINATIM_CACHE:
        cached_time, cached_data = _NOMINATIM_CACHE[cache_key]
        if now - cached_time < NOMINATIM_CACHE_TTL:
            logger.info("Serving Nominatim results from in-memory cache.")
            return cached_data

    # Enforce 1 request per second rate-limit
    elapsed = now - _LAST_REQUEST_TIMESTAMP
    if elapsed < 1.0:
        await httpx.AsyncClient().get("http://localhost", timeout=0.0) if False else None
        time.sleep(1.0 - elapsed)
    _LAST_REQUEST_TIMESTAMP = time.time()

    params = {
        "q": "recycling",
        "format": "json",
        "limit": 5,
        "viewbox": f"{lon-0.15},{lat+0.15},{lon+0.15},{lat-0.15}",
        "bounded": 1,
    }
    headers = {"User-Agent": NOMINATIM_USER_AGENT}

    try:
        async with httpx.AsyncClient(timeout=NOMINATIM_TIMEOUT) as client:
            resp = await client.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers)
            if resp.status_code == 200:
                results = resp.json()
                _NOMINATIM_CACHE[cache_key] = (now, results)
                return results
    except Exception as e:
        logger.warning(f"Nominatim lookup failed: {e}. Falling back to KSPCB database.")

    return []


def get_nearest_centers(
    user_lat: float | None = None,
    user_lon: float | None = None,
    class_name: str | None = None,
    limit: int = 3
) -> list[dict]:
    """
    Finds and ranks the closest authorized recycling facilities in Bengaluru.
    Filters by accepted e-waste categories and computes exact distance in km.
    """
    lat = user_lat if user_lat is not None else DEFAULT_BLR_LAT
    lon = user_lon if user_lon is not None else DEFAULT_BLR_LON

    ranked = []
    for center in _CENTERS:
        # Material filter
        if class_name and class_name != "other":
            accepted = center.get("categories_accepted", [])
            if class_name not in accepted:
                continue

        c_coords = center["coordinates"]
        dist = haversine_distance_km(lat, lon, c_coords["lat"], c_coords["lon"])

        entry = dict(center)
        entry["distance_km"] = round(dist, 2)
        ranked.append(entry)

    # Sort by proximity
    ranked.sort(key=lambda x: x["distance_km"])
    return ranked[:limit]
