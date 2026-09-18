"""File-backed check-in and status storage for the "Anlık Bilgi Akışı" MVP.

Same pattern as comments_store.py: temporary until PostgreSQL is wired up.
Two JSON files (checkins.json, status.json) are appended to so real
submissions persist across API restarts. No demo/example data is seeded
here - both stores start empty.

Honesty note (see docs/research/anlik-bilgi-akisi.md and CLAUDE.md "sahte
veri yasak" rule): seed venues only have an approximate district-center
coordinate (see frontend/src/lib/districts.js), not a real address. So the
GPS check here is deliberately loose (3km radius) and only ever produces a
soft `location_verified` flag - it never rejects a check-in. Callers must
not present this flag as a strong/precise verification.
"""

import html
import json
import math
import os
import threading
import uuid
from datetime import UTC, datetime, timedelta
from functools import lru_cache

_CHECKINS_PATH = os.path.join(os.path.dirname(__file__), "checkins.json")
_STATUS_PATH = os.path.join(os.path.dirname(__file__), "status.json")
_SEED_DIR = os.path.join(os.path.dirname(__file__), "seed")
_lock = threading.Lock()

# How recent a check-in must be to count towards the "how many people are
# here right now" proxy.
CHECKIN_ACTIVE_WINDOW_HOURS = 2
# How long a status update stays "fresh" before the frontend should show it
# as stale/grayed-out (research doc: 4-6h range, we pick the midpoint).
STATUS_STALE_HOURS = 5
# Loose radius for the "does this GPS position roughly match the venue's
# (approximate) location" check. Seed coordinates are district-center
# approximations, not real addresses, so this is intentionally generous.
LOCATION_VERIFY_RADIUS_KM = 3.0

STATUS_TAGS = ("Kalabalık", "Orta", "Sakin")

# Mirrors frontend/src/lib/districts.js DISTRICT_LATLNG - kept in sync
# manually since the frontend has no build step that shares this with Python.
_DISTRICT_LATLNG = {
    "Sarıyer": (41.167, 29.058),
    "Beşiktaş": (41.043, 29.009),
    "Şişli": (41.06, 28.988),
    "Beyoğlu": (41.037, 28.977),
    "Eyüpsultan": (41.048, 28.934),
    "Kağıthane": (41.079, 28.972),
    "Fatih": (41.019, 28.949),
    "Zeytinburnu": (40.995, 28.902),
    "Bakırköy": (40.982, 28.872),
    "Bahçelievler": (41.0, 28.859),
    "Bağcılar": (41.039, 28.856),
    "Esenler": (41.045, 28.879),
    "Bayrampaşa": (41.047, 28.907),
    "Gaziosmanpaşa": (41.065, 28.915),
    "Sultangazi": (41.106, 28.867),
    "Arnavutköy": (41.185, 28.74),
    "Başakşehir": (41.093, 28.802),
    "Küçükçekmece": (41.0, 28.775),
    "Avcılar": (40.98, 28.721),
    "Esenyurt": (41.033, 28.674),
    "Beylikdüzü": (41.0, 28.64),
    "Büyükçekmece": (41.02, 28.585),
    "Çatalca": (41.143, 28.461),
    "Silivri": (41.073, 28.247),
    "Beykoz": (41.124, 29.1),
    "Üsküdar": (41.027, 29.015),
    "Kadıköy": (40.99, 29.028),
    "Ataşehir": (40.992, 29.125),
    "Ümraniye": (41.016, 29.124),
    "Çekmeköy": (41.035, 29.198),
    "Sancaktepe": (41.0, 29.228),
    "Sultanbeyli": (40.962, 29.266),
    "Kartal": (40.907, 29.188),
    "Maltepe": (40.935, 29.156),
    "Pendik": (40.877, 29.253),
    "Tuzla": (40.816, 29.301),
    "Şile": (41.174, 29.612),
    "Adalar": (40.877, 29.125),
}
_DEFAULT_LATLNG = (41.02, 28.965)


@lru_cache(maxsize=1)
def _venue_areas() -> dict:
    """place_id -> area string, loaded once from the seed JSON files."""
    areas: dict[str, str] = {}
    for filename in ("places.json", "gurme.json", "hotels.json"):
        path = os.path.join(_SEED_DIR, filename)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for venue in json.load(f):
                if venue.get("id") and venue.get("area"):
                    areas[venue["id"]] = venue["area"]
    return areas


def _district_center(area: str | None) -> tuple[float, float]:
    if not area:
        return _DEFAULT_LATLNG
    for district, latlng in _DISTRICT_LATLNG.items():
        if district in area:
            return latlng
    return _DEFAULT_LATLNG


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r_km = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * r_km * math.asin(math.sqrt(a))


def _is_location_plausible(place_id: str, lat: float | None, lng: float | None) -> bool:
    """Soft, non-rejecting check - see module docstring honesty note."""
    if lat is None or lng is None:
        return False
    area = _venue_areas().get(place_id)
    center_lat, center_lng = _district_center(area)
    distance = _haversine_km(lat, lng, center_lat, center_lng)
    return distance <= LOCATION_VERIFY_RADIUS_KM


def _load(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_checkin(
    place_id: str,
    author: str,
    lat: float | None,
    lng: float | None,
    accuracy: float | None,
) -> dict:
    checkin = {
        "id": str(uuid.uuid4()),
        "place_id": place_id,
        "author": html.escape(author),
        "lat": lat,
        "lng": lng,
        "accuracy": accuracy,
        "location_verified": _is_location_plausible(place_id, lat, lng),
        "created_at": datetime.now(UTC).isoformat(),
    }
    with _lock:
        data = _load(_CHECKINS_PATH)
        data.setdefault(place_id, []).append(checkin)
        _save(_CHECKINS_PATH, data)
    return checkin


def count_recent_checkins(place_id: str, hours: int = CHECKIN_ACTIVE_WINDOW_HOURS) -> int:
    with _lock:
        data = _load(_CHECKINS_PATH)
    checkins = data.get(place_id, [])
    cutoff = datetime.now(UTC) - timedelta(hours=hours)
    count = 0
    for c in checkins:
        try:
            created = datetime.fromisoformat(c["created_at"])
        except (KeyError, ValueError):
            continue
        if created >= cutoff:
            count += 1
    return count


def add_status(place_id: str, author: str, tag: str, text: str) -> dict:
    status = {
        "id": str(uuid.uuid4()),
        "place_id": place_id,
        "author": html.escape(author),
        "tag": html.escape(tag),
        "text": html.escape(text) if text else "",
        "created_at": datetime.now(UTC).isoformat(),
    }
    with _lock:
        data = _load(_STATUS_PATH)
        data.setdefault(place_id, []).append(status)
        _save(_STATUS_PATH, data)
    return status


def list_status(place_id: str, stale_hours: int = STATUS_STALE_HOURS) -> list[dict]:
    with _lock:
        data = _load(_STATUS_PATH)
    entries = data.get(place_id, [])
    cutoff = datetime.now(UTC) - timedelta(hours=stale_hours)
    result = []
    for entry in entries:
        is_stale = True
        try:
            created = datetime.fromisoformat(entry["created_at"])
            is_stale = created < cutoff
        except (KeyError, ValueError):
            pass
        result.append({**entry, "is_stale": is_stale})
    return result
