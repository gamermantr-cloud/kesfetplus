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


class SelfHelpfulError(CommentError):
    """Raised when a user tries to mark their own comment as helpful."""


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
            "helpful_count": 0,
            "helpful_user_ids": [],
            **trust,
        }
        data.setdefault(place_id, []).append(comment)
        _save(data)
    return comment


def list_comments(
    place_id: str,
    include_hidden: bool = False,
    exclude_user_ids: set[str] | None = None,
    viewer_user_id: str | None = None,
) -> list[dict]:
    """List comments for a place.

    exclude_user_ids: when given (the requesting user's blocked_user_ids),
    comments whose author_user_id is in that set are filtered out
    server-side - hiding them only in the frontend is not enough (a blocked
    author's content must not be served to the blocker at all).

    viewer_user_id: the requesting user's own id (None if anonymous/not
    logged in). Two things depend on it, both for the "explainable trust
    score" feature (see docs/research/rakip-analizi-guncelleme-2026-09-30.md
    Bolum 3):
      - A comment whose review_status is "hidden" is still included here
        when it belongs to viewer_user_id (so the author can see their own
        held-back comment and why), but never for anyone else - the
        include_hidden=False filter below still applies to every other
        author's hidden comments exactly as before.
      - computed_trust_score (the raw numeric score / would-be formula
        leak) is never sent to any caller over this endpoint, author
        included. flagged_reason is kept only for the comment's own author
        and stripped (set to None) for every other viewer - moderators get
        the unredacted version through the separate
        list_hidden_comments()/list_all_reports() moderator-only paths, not
        this one.
    """
    with _lock:
        data = _load()
    comments = data.get(place_id, [])
    if not include_hidden:
        comments = [
            c
            for c in comments
            if c.get("review_status") != "hidden" or c.get("author_user_id") == viewer_user_id
        ]
    if exclude_user_ids:
        comments = [c for c in comments if c.get("author_user_id") not in exclude_user_ids]
    # Backfill helpful_count/helpful_user_ids for comments written before
    # this field existed (see add_comment) - never crash on a missing key,
    # just treat it as "nobody has marked this helpful yet".
    result = []
    for c in comments:
        item = {
            **c,
            "helpful_count": c.get("helpful_count", 0),
            "helpful_user_ids": c.get("helpful_user_ids", []),
        }
        item.pop("computed_trust_score", None)
        is_own = viewer_user_id is not None and item.get("author_user_id") == viewer_user_id
        if not is_own:
            item["flagged_reason"] = None
        result.append(item)
    return result


def count_all_comments() -> int:
    """Total comments stored across every place, regardless of
    review_status (0 if comments.json is missing/empty) - used by
    GET /moderation/stats in api/main.py."""
    with _lock:
        data = _load()
    return sum(len(comments) for comments in data.values())


def sum_helpful_by_place() -> dict[str, int]:
    """Sum of helpful_count across all *visible* comments, grouped by
    place_id - used by GET /places/popularity-scores (api/main.py) as part
    of the venue popularity signal (see checkins_store.sum_helpful_status_by_place
    for the same pattern applied to status updates). Hidden/flagged
    comments are excluded - content nobody actually saw shouldn't count
    toward a venue's popularity."""
    with _lock:
        data = _load()
    result: dict[str, int] = {}
    for place_id, comments in data.items():
        total = sum(
            c.get("helpful_count", 0) for c in comments if c.get("review_status") != "hidden"
        )
        if total:
            result[place_id] = total
    return result


def list_place_ids_with_comments() -> set[str]:
    """place_ids with at least one comment (any review_status) - used to
    compute GET /moderation/stats venues_with_activity in api/main.py
    (unioned there with checkins_store.list_place_ids_with_activity)."""
    with _lock:
        data = _load()
    return {place_id for place_id, comments in data.items() if comments}


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


def toggle_helpful_comment(place_id: str, comment_id: str, user_id: str) -> dict:
    """Mark/unmark a comment as "helpful" for user_id (see
    docs/research/anlik-bilgi-akisi.md "Teşvik Katmanı" - TripAdvisor's
    "helpful" signal). One user can only be counted once: calling this a
    second time removes the mark instead of adding a duplicate (the
    frontend's single "Faydalı" button toggles both ways via this same
    endpoint - see api/main.py).

    Marking your own comment is refused (CommentError -> 400): a helpful
    count is only meaningful as *other* people's signal, and self-marking
    would let anyone trivially inflate their own count.

    Old comments written before helpful_count/helpful_user_ids existed are
    backfilled to 0/[] here on first toggle (same default as list_comments).
    """
    with _lock:
        data = _load()
        for comment in data.get(place_id, []):
            if comment["id"] != comment_id:
                continue
            if comment.get("author_user_id") == user_id:
                raise SelfHelpfulError("Kendi yorumunu faydalı olarak işaretleyemezsin.")
            helpful_ids = list(comment.get("helpful_user_ids", []))
            if user_id in helpful_ids:
                helpful_ids.remove(user_id)
            else:
                helpful_ids.append(user_id)
            comment["helpful_user_ids"] = helpful_ids
            comment["helpful_count"] = len(helpful_ids)
            _save(data)
            return comment
    raise CommentError("Yorum bulunamadı.")


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
