"""File-backed comment storage.

Temporary until PostgreSQL is wired up (see docs/ARCHITECTURE.md). Comments
are appended to a JSON file so real submissions persist across API restarts
without needing a database yet. No demo/example comments are seeded here -
the store starts empty.
"""

import html
import json
import os
import threading
import uuid
from datetime import UTC, datetime

from database.trust_scoring import score_comment

_STORE_PATH = os.path.join(os.path.dirname(__file__), "comments.json")
_lock = threading.Lock()


def _load() -> dict:
    if not os.path.exists(_STORE_PATH):
        return {}
    with open(_STORE_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict) -> None:
    with open(_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_comment(
    place_id: str,
    author: str,
    text: str,
    lat: float | None = None,
    lng: float | None = None,
    accuracy: float | None = None,
) -> dict:
    """Store a new comment with a computed trust score.

    lat/lng/accuracy are optional (declining location permission is never
    penalized - see database/trust_scoring.py signal 2). Trust scoring is
    computed against the store's state *before* this comment is appended,
    so it can't compare/collide with itself.
    """
    escaped_author = html.escape(author)
    escaped_text = html.escape(text)

    with _lock:
        data = _load()
        trust = score_comment(place_id, escaped_author, escaped_text, lat, lng, data)
        comment = {
            "id": str(uuid.uuid4()),
            "place_id": place_id,
            "author": escaped_author,
            "text": escaped_text,
            "lat": lat,
            "lng": lng,
            "accuracy": accuracy,
            "created_at": datetime.now(UTC).isoformat(),
            **trust,
        }
        data.setdefault(place_id, []).append(comment)
        _save(data)
    return comment


def list_comments(place_id: str, include_hidden: bool = False) -> list[dict]:
    with _lock:
        data = _load()
    comments = data.get(place_id, [])
    if include_hidden:
        return comments
    return [c for c in comments if c.get("review_status") != "hidden"]
