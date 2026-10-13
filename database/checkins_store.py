"""PostgreSQL-backed check-in and status storage for the "Anlık Bilgi
Akışı" MVP.

Used to be two JSON files (checkins.json, status.json) guarded by a
threading.Lock - see database/README.md and git history for that version.
Now backed by the `checkins` and `status_updates` tables
(database/schema.sql); every write runs inside one DB transaction via
database/db.get_cursor(), which is what replaces the old lock (and, unlike
it, stays correct across multiple worker processes too).

Honesty note (see docs/research/anlik-bilgi-akisi.md and CLAUDE.md "sahte
veri yasak" rule): seed venues only have an approximate district-center
coordinate (see frontend/src/lib/districts.js), not a real address. So the
GPS check here is deliberately loose (3km radius) and only ever produces a
soft `location_verified` flag - it never rejects a check-in. Callers must
not present this flag as a strong/precise verification.

Every public function here keeps the exact same name/signature/return
shape it had as a JSON store, so api/main.py needed no changes at all.
"""

import html
import json
import logging
import math
import os
import uuid
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Any

from database.content_filter import check_content
from database.db import get_cursor
from database.push_notify import notify_new_status

logger = logging.getLogger(__name__)

_SEED_DIR = os.path.join(os.path.dirname(__file__), "seed")


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


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    """Row from `checkins`/`status_updates` -> the same dict shape the JSON
    stores used to produce - see comments_store._normalize_row for why
    created_at is converted back to an ISO-8601 string here."""
    out = dict(row)
    created_at = out.get("created_at")
    if isinstance(created_at, datetime):
        out["created_at"] = created_at.isoformat()
    return out


def add_checkin(
    place_id: str,
    author: str,
    lat: float | None,
    lng: float | None,
    accuracy: float | None,
    author_user_id: str | None = None,
) -> dict:
    checkin_id = str(uuid.uuid4())
    created_at = datetime.now(UTC)
    location_verified = _is_location_plausible(place_id, lat, lng)
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO checkins (
                id, place_id, author, author_user_id, lat, lng, accuracy,
                location_verified, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                checkin_id,
                place_id,
                html.escape(author),
                author_user_id,
                lat,
                lng,
                accuracy,
                location_verified,
                created_at,
            ),
        )
        row = cur.fetchone()
    if row is None:
        raise RuntimeError("INSERT ... RETURNING satır döndürmedi (beklenmeyen durum).")
    return _normalize_row(row)


def count_recent_checkins(place_id: str, hours: int = CHECKIN_ACTIVE_WINDOW_HOURS) -> int:
    cutoff = datetime.now(UTC) - timedelta(hours=hours)
    with get_cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) AS n FROM checkins WHERE place_id = %s AND created_at >= %s",
            (place_id, cutoff),
        )
        row = cur.fetchone()
    return row["n"] if row else 0


def _recent_checkin_user_ids(place_id: str, hours: int, exclude_user_id: str | None) -> set[str]:
    """user_ids who checked in at place_id within the last `hours` hours,
    excluding exclude_user_id (the person who just posted the status update
    that triggered this lookup) and any check-in with no real account
    attached. Deliberately reuses the existing check-in data - see
    NOTIFY_CHECKIN_WINDOW_HOURS - instead of introducing a new "follow this
    venue" subscription concept."""
    cutoff = datetime.now(UTC) - timedelta(hours=hours)
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT author_user_id FROM checkins
            WHERE place_id = %s AND created_at >= %s AND author_user_id IS NOT NULL
            """,
            (place_id, cutoff),
        )
        rows = cur.fetchall()
    return {row["author_user_id"] for row in rows if row["author_user_id"] != exclude_user_id}


def _notify_recent_checkins(place_id: str, tag: str, exclude_user_id: str | None) -> None:
    """Best-effort push fan-out to everyone who checked in at this venue
    recently (see _recent_checkin_user_ids), skipping the author. This must
    never be able to break add_status's real job (saving the status
    update) - database/push_notify.notify_new_status already never raises
    on its own, but this extra try/except is a second safety net around the
    lookup itself (e.g. a transient DB error)."""
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
    write is already durably committed, and can never raise back into this
    function.
    """
    content_check = check_content(text) if text else {"is_objectionable": False}
    status_id = str(uuid.uuid4())
    created_at = datetime.now(UTC)
    review_status = "hidden" if content_check["is_objectionable"] else "visible"
    flagged_reason = "objectionable_content" if content_check["is_objectionable"] else None
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO status_updates (
                id, place_id, author, author_user_id, tag, text, created_at,
                review_status, flagged_reason, helpful_count, helpful_user_ids
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s)
            RETURNING *
            """,
            (
                status_id,
                place_id,
                html.escape(author),
                author_user_id,
                html.escape(tag),
                html.escape(text) if text else "",
                created_at,
                review_status,
                flagged_reason,
                [],
            ),
        )
        row = cur.fetchone()
    if row is None:
        raise RuntimeError("INSERT ... RETURNING satır döndürmedi (beklenmeyen durum).")
    status = _normalize_row(row)
    if status["review_status"] == "visible":
        _notify_recent_checkins(place_id, status["tag"], author_user_id)
    return status


def list_status(
    place_id: str,
    stale_hours: int = STATUS_STALE_HOURS,
    exclude_user_ids: set[str] | None = None,
    include_hidden: bool = False,
    viewer_user_id: str | None = None,
) -> list[dict]:
    """List status updates for a place.

    exclude_user_ids: when given (the requesting user's blocked_user_ids),
    entries whose author_user_id is in that set are filtered out
    server-side - see comments_store.list_comments for the same pattern.

    include_hidden: like comments_store.list_comments, entries flagged by
    database/content_filter.py (review_status="hidden") are excluded by
    default - the content is still stored, just not served publicly.

    viewer_user_id: the requesting user's own id (None if anonymous). Same
    "explainable trust score" rules as comments_store.list_comments - a
    hidden entry is still returned when it belongs to viewer_user_id (so the
    author can see it and why), and flagged_reason is stripped for every
    entry that isn't viewer_user_id's own (status updates have no
    computed_trust_score field to begin with - see add_status - so there's
    nothing numeric to strip here).
    """
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM status_updates WHERE place_id = %s ORDER BY created_at",
            (place_id,),
        )
        entries = [_normalize_row(r) for r in cur.fetchall()]
    if not include_hidden:
        entries = [
            e
            for e in entries
            if e.get("review_status") != "hidden" or e.get("author_user_id") == viewer_user_id
        ]
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
        is_own = viewer_user_id is not None and entry.get("author_user_id") == viewer_user_id
        result.append(
            {
                **entry,
                "is_stale": is_stale,
                "flagged_reason": entry.get("flagged_reason") if is_own else None,
            }
        )
    return result


def count_all_checkins() -> int:
    """Total check-ins stored across every place (0 if the table is empty)
    - used by GET /moderation/stats in api/main.py."""
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM checkins")
        row = cur.fetchone()
    return row["n"] if row else 0


def count_checkins_by_place() -> dict[str, int]:
    """Total (all-time) check-in count per place_id - used by
    GET /places/popularity-scores in api/main.py to build a relevance/
    sıralama signal for the venue list without an extra HTTP round-trip per
    venue. Unlike count_recent_checkins (per-place, restricted to
    CHECKIN_ACTIVE_WINDOW_HOURS - "who's here right now"), this is
    unrestricted by time, since popularity ranking should reflect all-time
    activity, not just the last couple of hours."""
    with get_cursor() as cur:
        cur.execute("SELECT place_id, COUNT(*) AS n FROM checkins GROUP BY place_id")
        rows = cur.fetchall()
    return {row["place_id"]: row["n"] for row in rows}


def sum_helpful_status_by_place() -> dict[str, int]:
    """Sum of helpful_count across all *visible* status updates, grouped by
    place_id - used by GET /places/popularity-scores (api/main.py) as part
    of the venue popularity signal. Hidden/flagged entries are excluded,
    same rule list_status applies by default (content nobody actually saw
    shouldn't count toward a venue's popularity)."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT place_id, SUM(helpful_count) AS total
            FROM status_updates
            WHERE review_status != 'hidden'
            GROUP BY place_id
            HAVING SUM(helpful_count) > 0
            """
        )
        rows = cur.fetchall()
    return {row["place_id"]: row["total"] for row in rows}


def count_all_status() -> int:
    """Total status updates stored across every place, regardless of
    review_status (0 if the table is empty) - used by GET /moderation/stats
    in api/main.py."""
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM status_updates")
        row = cur.fetchone()
    return row["n"] if row else 0


def list_place_ids_with_activity() -> set[str]:
    """place_ids with at least one check-in or status update - used (unioned
    with comments_store.list_place_ids_with_comments) to compute
    GET /moderation/stats venues_with_activity in api/main.py."""
    with get_cursor() as cur:
        cur.execute("SELECT DISTINCT place_id FROM checkins")
        checkin_rows = cur.fetchall()
        cur.execute("SELECT DISTINCT place_id FROM status_updates")
        status_rows = cur.fetchall()
    place_ids = {row["place_id"] for row in checkin_rows}
    place_ids |= {row["place_id"] for row in status_rows}
    return place_ids


def list_hidden_status() -> list[dict]:
    """Every status update across every place that's hidden or flagged -
    moderator-only visibility (see comments_store.list_hidden_comments for
    the same pattern; checkins have no review_status so they're excluded)."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT * FROM status_updates
            WHERE review_status = 'hidden' OR flagged_reason IS NOT NULL
            ORDER BY created_at
            """
        )
        rows = cur.fetchall()
    return [_normalize_row(r) for r in rows]


def toggle_helpful_status(place_id: str, status_id: str, user_id: str) -> dict:
    """Mark/unmark a status update as "helpful" for user_id - same toggle
    semantics as comments_store.toggle_helpful_comment (one mark per user,
    calling again removes it, self-marking refused with StatusError -> 400).
    See that function's docstring for the full reasoning, including why
    `SELECT ... FOR UPDATE` is used here too."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM status_updates WHERE place_id = %s AND id = %s FOR UPDATE",
            (place_id, status_id),
        )
        row = cur.fetchone()
        if row is None:
            raise StatusError("Durum güncellemesi bulunamadı.")
        if row.get("author_user_id") == user_id:
            raise SelfHelpfulError("Kendi durumunu faydalı olarak işaretleyemezsin.")
        helpful_ids = list(row.get("helpful_user_ids") or [])
        if user_id in helpful_ids:
            helpful_ids.remove(user_id)
        else:
            helpful_ids.append(user_id)
        cur.execute(
            """
            UPDATE status_updates SET helpful_user_ids = %s, helpful_count = %s
            WHERE place_id = %s AND id = %s
            RETURNING *
            """,
            (helpful_ids, len(helpful_ids), place_id, status_id),
        )
        updated = cur.fetchone()
    if updated is None:
        raise RuntimeError("UPDATE ... RETURNING satır döndürmedi (beklenmeyen durum).")
    return _normalize_row(updated)


def count_user_statuses(user_id: str, include_hidden: bool = False) -> int:
    """Real-time count of how many status updates this user has posted -
    the sole input for the "Gözcü" badge (GOZCU_THRESHOLD, see api/main.py
    GET /users/{id}/stats). Deliberately NOT cached/stored anywhere: it is
    recomputed from the table on every call, so the badge can never drift
    from the real data (see CLAUDE.md "sahte veri yasak" / MUTLAK KURAL).

    include_hidden=False (default) excludes status updates the content
    filter hid (review_status == "hidden") - content that was never
    actually shown to anyone shouldn't count toward a reputation badge.
    """
    query = "SELECT COUNT(*) AS n FROM status_updates WHERE author_user_id = %s"
    params: tuple[str, ...] = (user_id,)
    if not include_hidden:
        query += " AND review_status != 'hidden'"
    with get_cursor() as cur:
        cur.execute(query, params)
        row = cur.fetchone()
    return row["n"] if row else 0


def restore_status(status_id: str) -> dict:
    """Moderator override: set a status update's review_status back to
    "visible". Raises StatusError if no status update with this id exists."""
    with get_cursor() as cur:
        cur.execute(
            """
            UPDATE status_updates SET review_status = 'visible', flagged_reason = NULL
            WHERE id = %s
            RETURNING *
            """,
            (status_id,),
        )
        row = cur.fetchone()
    if row is None:
        raise StatusError("Durum güncellemesi bulunamadı.")
    return _normalize_row(row)
