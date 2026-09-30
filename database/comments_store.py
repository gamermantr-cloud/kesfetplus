"""File-backed comment storage.

Temporary until PostgreSQL is wired up (see docs/ARCHITECTURE.md). Comments
are appended to a JSON file so real submissions persist across API restarts
without needing a database yet. No demo/example comments are seeded here -
the store starts empty.

KNOWN LIMITATION: the threading.Lock here only guards against concurrent
writes *within a single process*. It provides no safety if the API is ever
run with multiple worker processes (e.g. `uvicorn --workers N`, gunicorn)
pointed at the same JSON files - concurrent writes from different processes
can interleave and corrupt comments.json. Fine for today's single-worker
dev/small-scale deployment; must be resolved (real DB, or a cross-process
lock) before scaling to multiple workers.
"""

import html
import json
import os
import threading
import uuid
from datetime import UTC, datetime

from database.content_filter import check_content
from database.trust_scoring import score_comment

_STORE_PATH = os.path.join(os.path.dirname(__file__), "comments.json")
_lock = threading.Lock()


class CommentError(Exception):
    """Raised when a comment lookup (e.g. restore) doesn't match a real id."""


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
    author_user_id: str | None = None,
) -> dict:
    """Store a new comment with a computed trust score.

    lat/lng/accuracy are optional (declining location permission is never
    penalized - see database/trust_scoring.py signal 2). Trust scoring is
    computed against the store's state *before* this comment is appended,
    so it can't compare/collide with itself.

    author_user_id ties the comment to a real account (database/users_store.py)
    for ownership/blocking. It's optional/None for comments written before
    the account system existed - old records without it are simply never
    matched by a blocked_user_ids filter, never crash on it (see
    list_comments's exclude_user_ids).

    Content is also run through database/content_filter.py (App Store
    Guideline 1.2 - UGC moderation). This is a separate check from trust
    scoring: an objectionable comment is still stored (never silently
    dropped, matching the project's "be transparent" stance) but forced to
    review_status="hidden" regardless of its trust score - see
    _apply_content_filter below. Only the boolean result is ever used; the
    matched terms themselves are never logged or stored.
    """
    escaped_author = html.escape(author)
    escaped_text = html.escape(text)
    content_check = check_content(text)

    with _lock:
        data = _load()
        trust = score_comment(place_id, escaped_author, escaped_text, lat, lng, data)
        if content_check["is_objectionable"]:
            trust["review_status"] = "hidden"
            trust["flagged_reason"] = "objectionable_content"
        comment = {
            "id": str(uuid.uuid4()),
            "place_id": place_id,
            "author": escaped_author,
            "author_user_id": author_user_id,
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


def list_comments(
    place_id: str,
    include_hidden: bool = False,
    exclude_user_ids: set[str] | None = None,
) -> list[dict]:
    """List comments for a place.

    exclude_user_ids: when given (the requesting user's blocked_user_ids),
    comments whose author_user_id is in that set are filtered out
    server-side - hiding them only in the frontend is not enough (a blocked
    author's content must not be served to the blocker at all).
    """
    with _lock:
        data = _load()
    comments = data.get(place_id, [])
    if not include_hidden:
        comments = [c for c in comments if c.get("review_status") != "hidden"]
    if exclude_user_ids:
        comments = [c for c in comments if c.get("author_user_id") not in exclude_user_ids]
    return comments


def list_hidden_comments() -> list[dict]:
    """Every comment across every place that's hidden or flagged -
    moderator-only visibility (see api/main.py get_current_moderator). Until
    now nothing surfaced these; this is the "moderation isn't blind" fix."""
    with _lock:
        data = _load()
    hidden = []
    for comments in data.values():
        for comment in comments:
            if comment.get("review_status") == "hidden" or comment.get("flagged_reason"):
                hidden.append(comment)
    return hidden


def restore_comment(comment_id: str) -> dict:
    """Moderator override: set a comment's review_status back to "visible"
    (e.g. the content filter false-positived). Raises CommentError if no
    comment with this id exists in any place."""
    with _lock:
        data = _load()
        for comments in data.values():
            for comment in comments:
                if comment["id"] == comment_id:
                    comment["review_status"] = "visible"
                    comment["flagged_reason"] = None
                    _save(data)
                    return comment
    raise CommentError("Yorum bulunamadı.")
