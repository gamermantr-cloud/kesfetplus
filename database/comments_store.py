"""File-backed comment storage.

Temporary until PostgreSQL is wired up (see docs/ARCHITECTURE.md). Comments
are appended to a JSON file so real submissions persist across API restarts
without needing a database yet. No demo/example comments are seeded here -
the store starts empty.
"""

import json
import os
import threading
import uuid
from datetime import UTC, datetime

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


def add_comment(place_id: str, author: str, text: str) -> dict:
    comment = {
        "id": str(uuid.uuid4()),
        "place_id": place_id,
        "author": author,
        "text": text,
        "created_at": datetime.now(UTC).isoformat(),
    }
    with _lock:
        data = _load()
        data.setdefault(place_id, []).append(comment)
        _save(data)
    return comment


def list_comments(place_id: str) -> list[dict]:
    with _lock:
        data = _load()
    return data.get(place_id, [])
