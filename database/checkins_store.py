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

KNOWN LIMITATION: same as comments_store.py - the threading.Lock only
guards a single process. Running the API with multiple workers against
these same JSON files risks corrupting checkins.json/status.json. Must be
resolved (real DB, or cross-process locking) before a multi-worker deploy.
"""

import html
import json
import logging
import math
import os
import threading
import uuid
from datetime import UTC, datetime, timedelta
from functools import lru_cache

from database.content_filter import check_content
from database.push_notify import notify_new_status

logger = logging.getLogger(__name__)

_CHECKINS_PATH = os.path.join(os.path.dirname(__file__), "checkins.json")
_STATUS_PATH = os.path.join(os.path.dirname(__file__), "status.json")
_SEED_DIR = os.path.join(os.path.dirname(__file__), "seed")
_lock = threading.Lock()


class StatusError(Exception):
    """Raised when a status-update lookup (e.g. restore) doesn't match a
    real id."""


class SelfHelpfulError(StatusError):
    """Raised when a user tries to mark their own status update as helpful."""


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

# "Gözcü" badge threshold (docs/research/anlik-bilgi-akisi.md "Teşvik
# Katmanı"): 10+ status updates. Never stored on the user record - always
# recomputed from status.json (see count_user_statuses) so it can't drift
# from the real data.
GOZCU_THRESHOLD = 10

# How far back to look for "other people who were just at this venue" when a
# new status update goes out - see _recent_checkin_user_ids / add_status.
# Matches the task's "same venue, checked in within the last 6 hours" rule;
# deliberately reuses the existing check-in data instead of a new "follow a
# venue" system.
NOTIFY_CHECKIN_WINDOW_HOURS = 6

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


@lru_cache(maxsize=1)
def _venue_names() -> dict:
    """place_id -> display name, loaded once from the seed JSON files - used
    to write a human-readable push notification body (see
    database/push_notify.py notify_new_status)."""
    names: dict[str, str] = {}
    for filename in ("places.json", "gurme.json", "hotels.json"):
        path = os.path.join(_SEED_DIR, filename)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for venue in json.load(f):
                if venue.get("id") and venue.get("name"):
                    names[venue["id"]] = venue["name"]
    return names


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
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
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
    author_user_id: str | None = None,
) -> dict:
    checkin = {
        "id": str(uuid.uuid4()),
        "place_id": place_id,
        "author": html.escape(author),
        "author_user_id": author_user_id,
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


def _recent_checkin_user_ids(place_id: str, hours: int, exclude_user_id: str | None) -> set[str]:
    """user_ids who checked in at place_id within the last `hours` hours,
    excluding exclude_user_id (the person who just posted the status update
    that triggered this lookup) and any check-in with no real account
    attached. Deliberately reuses the existing check-in data - see
    NOTIFY_CHECKIN_WINDOW_HOURS - instead of introducing a new "follow this
    venue" subscription concept."""
    with _lock:
        data = _load(_CHECKINS_PATH)
    checkins = data.get(place_id, [])
    cutoff = datetime.now(UTC) - timedelta(hours=hours)
    user_ids: set[str] = set()
    for c in checkins:
        user_id = c.get("author_user_id")
        if not user_id or user_id == exclude_user_id:
            continue
        try:
            created = datetime.fromisoformat(c["created_at"])
        except (KeyError, ValueError):
            continue
        if created >= cutoff:
            user_ids.add(user_id)
    return user_ids


def _notify_recent_checkins(place_id: str, tag: str, exclude_user_id: str | None) -> None:
    """Best-effort push fan-out to everyone who checked in at this venue
    recently (see _recent_checkin_user_ids), skipping the author. This must
    never be able to break add_status's real job (saving the status
    update) - database/push_notify.notify_new_status already never raises
    on its own, but this extra try/except is a second safety net around the
    lookup itself (e.g. a corrupted checkins.json)."""
    try:
        recipient_ids = _recent_checkin_user_ids(
            place_id, NOTIFY_CHECKIN_WINDOW_HOURS, exclude_user_id
        )
        if not recipient_ids:
            return
        venue_name = _venue_names().get(place_id, "bir mekan")
        notify_new_status(place_id, venue_name, tag, recipient_ids)
    except Exception:  # pragma: no cover - safety net, must never break add_status
        logger.exception("Anlık durum push bildirimi gönderilirken beklenmeyen hata.")


def add_status(
    place_id: str, author: str, tag: str, text: str, author_user_id: str | None = None
) -> dict:
    """Store a status update.

    `text` is optional/free-form (the tag alone is enough to post), so it's
    run through database/content_filter.py (App Store Guideline 1.2 - UGC
    moderation) the same way comments_store.add_comment does: an
    objectionable status is still stored (never silently dropped) but forced
    to review_status="hidden" - see list_status's default filtering. Only
    the boolean result is used; matched terms are never logged or stored.

    If the update is actually visible, this also fans out a real Web Push
    notification (database/push_notify.py) to anyone who checked in at the
    same place_id within the last NOTIFY_CHECKIN_WINDOW_HOURS hours (except
    the author) - see _notify_recent_checkins. That send happens after the
    write is already durably saved, and can never raise back into this
    function.
    """
    content_check = check_content(text) if text else {"is_objectionable": False}
    status: dict = {
        "id": str(uuid.uuid4()),
        "place_id": place_id,
        "author": html.escape(author),
        "author_user_id": author_user_id,
        "tag": html.escape(tag),
        "text": html.escape(text) if text else "",
        "created_at": datetime.now(UTC).isoformat(),
        "review_status": "hidden" if content_check["is_objectionable"] else "visible",
        "flagged_reason": "objectionable_content" if content_check["is_objectionable"] else None,
        "helpful_count": 0,
        "helpful_user_ids": [],
    }
    with _lock:
        data = _load(_STATUS_PATH)
        data.setdefault(place_id, []).append(status)
        _save(_STATUS_PATH, data)
    if status["review_status"] == "visible":
        _notify_recent_checkins(place_id, status["tag"], author_user_id)
    return status


def list_status(
    place_id: str,
    stale_hours: int = STATUS_STALE_HOURS,
    exclude_user_ids: set[str] | None = None,
    include_hidden: bool = False,
) -> list[dict]:
    """List status updates for a place.

    exclude_user_ids: when given (the requesting user's blocked_user_ids),
    entries whose author_user_id is in that set are filtered out
    server-side - see comments_store.list_comments for the same pattern.

    include_hidden: like comments_store.list_comments, entries flagged by
    database/content_filter.py (review_status="hidden") are excluded by
    default - the content is still stored, just not served publicly.
    """
    with _lock:
        data = _load(_STATUS_PATH)
    entries = data.get(place_id, [])
    if not include_hidden:
        entries = [e for e in entries if e.get("review_status") != "hidden"]
    if exclude_user_ids:
        entries = [e for e in entries if e.get("author_user_id") not in exclude_user_ids]
    cutoff = datetime.now(UTC) - timedelta(hours=stale_hours)
    result = []
    for entry in entries:
        is_stale = True
        try:
            created = datetime.fromisoformat(entry["created_at"])
            is_stale = created < cutoff
        except (KeyError, ValueError):
            pass
        # Backfill helpful_count/helpful_user_ids for status updates written
        # before this field existed (same pattern as comments_store.list_comments).
        result.append(
            {
                **entry,
                "is_stale": is_stale,
                "helpful_count": entry.get("helpful_count", 0),
                "helpful_user_ids": entry.get("helpful_user_ids", []),
            }
        )
    return result


def list_hidden_status() -> list[dict]:
    """Every status update across every place that's hidden or flagged -
    moderator-only visibility (see comments_store.list_hidden_comments for
    the same pattern; checkins have no review_status so they're excluded)."""
    with _lock:
        data = _load(_STATUS_PATH)
    hidden = []
    for entries in data.values():
        for entry in entries:
            if entry.get("review_status") == "hidden" or entry.get("flagged_reason"):
                hidden.append(entry)
    return hidden


def toggle_helpful_status(place_id: str, status_id: str, user_id: str) -> dict:
    """Mark/unmark a status update as "helpful" for user_id - same toggle
    semantics as comments_store.toggle_helpful_comment (one mark per user,
    calling again removes it, self-marking refused with StatusError -> 400).
    See that function's docstring for the full reasoning."""
    with _lock:
        data = _load(_STATUS_PATH)
        for entry in data.get(place_id, []):
            if entry["id"] != status_id:
                continue
            if entry.get("author_user_id") == user_id:
                raise SelfHelpfulError("Kendi durumunu faydalı olarak işaretleyemezsin.")
            helpful_ids = list(entry.get("helpful_user_ids", []))
            if user_id in helpful_ids:
                helpful_ids.remove(user_id)
            else:
                helpful_ids.append(user_id)
            entry["helpful_user_ids"] = helpful_ids
            entry["helpful_count"] = len(helpful_ids)
            _save(_STATUS_PATH, data)
            return entry
    raise StatusError("Durum güncellemesi bulunamadı.")


def count_user_statuses(user_id: str, include_hidden: bool = False) -> int:
    """Real-time count of how many status updates this user has posted -
    the sole input for the "Gözcü" badge (GOZCU_THRESHOLD, see api/main.py
    GET /users/{id}/stats). Deliberately NOT cached/stored anywhere: it is
    recomputed from status.json on every call, so the badge can never drift
    from the real data (see CLAUDE.md "sahte veri yasak" / MUTLAK KURAL).

    include_hidden=False (default) excludes status updates the content
    filter hid (review_status == "hidden") - content that was never
    actually shown to anyone shouldn't count toward a reputation badge.
    """
    with _lock:
        data = _load(_STATUS_PATH)
    count = 0
    for entries in data.values():
        for entry in entries:
            if entry.get("author_user_id") != user_id:
                continue
            if not include_hidden and entry.get("review_status") == "hidden":
                continue
            count += 1
    return count


def restore_status(status_id: str) -> dict:
    """Moderator override: set a status update's review_status back to
    "visible". Raises StatusError if no status update with this id exists
    in any place."""
    with _lock:
        data = _load(_STATUS_PATH)
        for entries in data.values():
            for entry in entries:
                if entry["id"] == status_id:
                    entry["review_status"] = "visible"
                    entry["flagged_reason"] = None
                    _save(_STATUS_PATH, data)
                    return entry
    raise StatusError("Durum güncellemesi bulunamadı.")
