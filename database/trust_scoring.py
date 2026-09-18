"""Rule-based trust-scoring MVP for comments.

Implements the scoring logic proposed in docs/research/trust-scoring.md
("Kesfet Plus icin MVP Trust-Scoring Onerisi"). The research doc proposes
4 signals; only 3 are implemented here.

Signal 1 - hesap yasi / e-posta / telefon dogrulama - is NOT IMPLEMENTED.
Keşfet Plus has no user account system at all: a comment is just a free-text
name typed into a form, with no signup, no email, no phone, nothing to
verify and no history to measure "account age" against. There is nothing
real to compute for this signal, so instead of inventing a fake proxy for
it (forbidden by CLAUDE.md's "sahte veri yasak" rule), it is left neutral:
every comment gets the exact same fixed contribution (ACCOUNT_SIGNAL_SCORE)
toward the total, so it never rewards or penalizes any one author relative
to another. If a real account system is ever added, this is the slot where
account_age/email_verified/phone_verified would plug in.

Signals 2-4 (all implemented below):
  2. Konum tutarligi   - reuses checkins_store's district-center/haversine
                          helpers (same 3km loose radius, same honesty
                          caveat: seed venues only have approximate
                          district-center coordinates, not real addresses).
  3. Metin benzerligi  - stdlib difflib.SequenceMatcher against other
                          comments (same place, falling back to the most
                          recent comments platform-wide if the place has
                          too few to compare against). No extra dependency.
  4. Gonderim hizi (velocity) - same-author burst in the last hour, or
                          many-different-authors burst on the same place
                          in the last 10 minutes.

Puanlama mantigi (trust-scoring.md #5): computed_trust_score >= 70 ->
dogrudan yayinlanir ("visible"). 40-70 -> yayinlanir ama golgeli
"topluluk incelemesi bekliyor" rozetiyle ("pending_review"). <40 ->
moderasyon kuyruguna duser, otomatik yayinlanmaz ("hidden").
"""

from __future__ import annotations

import difflib
from datetime import UTC, datetime, timedelta
from typing import Any

from database.checkins_store import _district_center, _haversine_km, _venue_areas

# ---------------------------------------------------------------------------
# Weights. Total max = 100 (30 + 30 + 25 + 15).
# ---------------------------------------------------------------------------

# Signal 1 - not applicable (see module docstring). Fixed/neutral: identical
# for every comment, so it can't distinguish "trustworthy" from "not".
ACCOUNT_SIGNAL_SCORE = 30.0

# Signal 2 - location consistency.
LOCATION_SIGNAL_MAX = 30.0
LOCATION_SIGNAL_NEUTRAL = LOCATION_SIGNAL_MAX / 2  # no GPS permission given
LOCATION_RADIUS_KM = 3.0  # matches checkins_store.LOCATION_VERIFY_RADIUS_KM

# Signal 3 - text similarity / duplicate detection.
TEXT_SIGNAL_MAX = 25.0
TEXT_SIMILARITY_THRESHOLD = 0.85
TEXT_SIMILARITY_FALLBACK_POOL = 30  # "genel olarak son N yorum"
TEXT_SIMILARITY_MIN_SAME_PLACE = 3  # below this, also pull in the fallback pool

# Signal 4 - posting velocity.
VELOCITY_SIGNAL_MAX = 15.0
VELOCITY_AUTHOR_WINDOW_MINUTES = 60
VELOCITY_AUTHOR_MAX_COMMENTS = 3
VELOCITY_PLACE_WINDOW_MINUTES = 10
VELOCITY_PLACE_MAX_AUTHORS = 5

# Overall thresholds.
TRUST_VISIBLE_THRESHOLD = 70.0
TRUST_PENDING_THRESHOLD = 40.0


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _location_score(
    place_id: str, lat: float | None, lng: float | None
) -> tuple[float, str | None]:
    """Signal 2. No GPS given -> neutral (never penalized for declining
    location permission). GPS given but far from the venue -> 0 + flag."""
    if lat is None or lng is None:
        return LOCATION_SIGNAL_NEUTRAL, None
    area = _venue_areas().get(place_id)
    center_lat, center_lng = _district_center(area)
    distance = _haversine_km(lat, lng, center_lat, center_lng)
    if distance <= LOCATION_RADIUS_KM:
        return LOCATION_SIGNAL_MAX, None
    return 0.0, "unverified_location"


def _text_similarity_score(text: str, comparison_texts: list[str]) -> tuple[float, str | None]:
    """Signal 3. Highest SequenceMatcher ratio against a comparison pool
    (which only ever holds comments already stored *before* this one, so
    an exact match here is a real duplicate, not a self-comparison
    artifact); above threshold -> likely copy-paste/template/bot text."""
    best = 0.0
    for other in comparison_texts:
        if not other:
            continue
        ratio = difflib.SequenceMatcher(None, text, other).ratio()
        if ratio > best:
            best = ratio
    if best > TEXT_SIMILARITY_THRESHOLD:
        return 0.0, "duplicate_text"
    return TEXT_SIGNAL_MAX, None


def _velocity_score(
    author: str, place_id: str, data: dict[str, list[dict[str, Any]]], now: datetime
) -> tuple[float, str | None]:
    """Signal 4. Same-author burst (any place) in the last hour, or a
    many-different-authors burst on this one place in the last 10 minutes."""
    author_window_start = now - timedelta(minutes=VELOCITY_AUTHOR_WINDOW_MINUTES)
    author_count = 0
    for comments in data.values():
        for c in comments:
            if c.get("author") != author:
                continue
            created = _parse_dt(c.get("created_at"))
            if created is not None and created >= author_window_start:
                author_count += 1
    if author_count > VELOCITY_AUTHOR_MAX_COMMENTS:
        return 0.0, "velocity_spike"

    place_window_start = now - timedelta(minutes=VELOCITY_PLACE_WINDOW_MINUTES)
    recent_authors = set()
    for c in data.get(place_id, []):
        created = _parse_dt(c.get("created_at"))
        if created is not None and created >= place_window_start:
            recent_authors.add(c.get("author"))
    if len(recent_authors) > VELOCITY_PLACE_MAX_AUTHORS:
        return 0.0, "velocity_spike"

    return VELOCITY_SIGNAL_MAX, None


def _review_status(total: float) -> str:
    if total >= TRUST_VISIBLE_THRESHOLD:
        return "visible"
    if total >= TRUST_PENDING_THRESHOLD:
        return "pending_review"
    return "hidden"


def score_comment(
    place_id: str,
    author: str,
    text: str,
    lat: float | None,
    lng: float | None,
    data: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    """Compute the trust score for a new comment (not yet appended to `data`).

    `author`/`text` should already be html-escaped (same form they'll be
    stored/compared in), and `data` is the full place_id -> [comment, ...]
    store, loaded *before* this comment is added.
    """
    now = datetime.now(UTC)
    reasons: list[str] = []

    location_score, location_reason = _location_score(place_id, lat, lng)
    if location_reason:
        reasons.append(location_reason)

    same_place_texts = [c.get("text", "") for c in data.get(place_id, [])]
    comparison_texts = list(same_place_texts)
    if len(same_place_texts) < TEXT_SIMILARITY_MIN_SAME_PLACE:
        all_comments = [c for comments in data.values() for c in comments]
        all_comments.sort(key=lambda c: c.get("created_at", ""))
        fallback_pool = all_comments[-TEXT_SIMILARITY_FALLBACK_POOL:]
        comparison_texts += [c.get("text", "") for c in fallback_pool]

    text_score, text_reason = _text_similarity_score(text, comparison_texts)
    if text_reason:
        reasons.append(text_reason)

    velocity_score, velocity_reason = _velocity_score(author, place_id, data, now)
    if velocity_reason:
        reasons.append(velocity_reason)

    total = round(ACCOUNT_SIGNAL_SCORE + location_score + text_score + velocity_score, 1)

    return {
        "computed_trust_score": total,
        "flagged_reason": ", ".join(reasons) if reasons else None,
        "review_status": _review_status(total),
    }
