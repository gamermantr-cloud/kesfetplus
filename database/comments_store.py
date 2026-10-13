"""PostgreSQL-backed comment storage.

Used to be a JSON file (database/comments.json) guarded by a
threading.Lock - see database/README.md and git history for that version.
Now backed by the `comments` table (database/schema.sql); every write runs
inside one DB transaction via database/db.get_cursor(), which is what
replaces the old lock (and, unlike it, stays correct across multiple
worker processes too).

Every public function here keeps the exact same name/signature/return
shape it had as a JSON store, so api/main.py needed no changes at all.
"""

from __future__ import annotations

import html
import uuid
from datetime import UTC, datetime
from typing import Any

from database.content_filter import check_content
from database.db import get_cursor
from database.trust_scoring import score_comment


class CommentError(Exception):
    """Raised when a comment lookup (e.g. restore) doesn't match a real id."""


class SelfHelpfulError(CommentError):
    """Raised when a user tries to mark their own comment as helpful."""


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    """Row from the `comments` table -> the same dict shape the JSON store
    used to produce. The only real difference is `created_at`: psycopg
    hands back a timezone-aware datetime for a TIMESTAMPTZ column, but the
    rest of this codebase (trust_scoring.py's velocity signal,
    checkins_store.py's staleness checks, etc.) expects an ISO-8601
    string - the same thing `datetime.now(UTC).isoformat()` used to write
    to the JSON file - so it's converted back here, once, at the boundary."""
    out = dict(row)
    created_at = out.get("created_at")
    if isinstance(created_at, datetime):
        out["created_at"] = created_at.isoformat()
    return out


def _all_comments_by_place() -> dict[str, list[dict[str, Any]]]:
    """Every comment in the table, grouped by place_id - the same shape
    database/trust_scoring.score_comment expects for its `data` argument
    (it needs to see comments across *every* place for the velocity-signal
    "same author, any place" check, and a fallback text-similarity pool
    when a place has too few comments of its own).

    This is a full-table scan, same cost profile the old JSON version had
    (it loaded the whole comments.json on every new comment too) - fine at
    today's scale (a handful of real submissions). If comment volume ever
    makes this a real bottleneck, the fix is targeted queries (comments in
    the last hour for this author, last N platform-wide, etc.) instead of
    this helper - not before it's an actual, measured problem (see
    docs/research/turkiye-pazar-teknik-mimari.md Bölüm 3's over-engineering
    warning)."""
    with get_cursor() as cur:
        cur.execute("SELECT place_id, author, text, created_at FROM comments")
        rows = [_normalize_row(r) for r in cur.fetchall()]
    data: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        data.setdefault(row["place_id"], []).append(row)
    return data


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
    computed against every comment already in the table *before* this one
    is inserted, so it can't compare/collide with itself.

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

    data = _all_comments_by_place()
    trust = score_comment(place_id, escaped_author, escaped_text, lat, lng, data)
    if content_check["is_objectionable"]:
        trust["review_status"] = "hidden"
        trust["flagged_reason"] = "objectionable_content"

    comment_id = str(uuid.uuid4())
    created_at = datetime.now(UTC)
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO comments (
                id, place_id, author, author_user_id, text, lat, lng, accuracy,
                created_at, helpful_count, helpful_user_ids,
                computed_trust_score, flagged_reason, review_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                comment_id,
                place_id,
                escaped_author,
                author_user_id,
                escaped_text,
                lat,
                lng,
                accuracy,
                created_at,
                [],
                trust["computed_trust_score"],
                trust["flagged_reason"],
                trust["review_status"],
            ),
        )
        row = cur.fetchone()
    if row is None:
        raise RuntimeError("INSERT ... RETURNING satır döndürmedi (beklenmeyen durum).")
    return _normalize_row(row)


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
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM comments WHERE place_id = %s ORDER BY created_at",
            (place_id,),
        )
        comments = [_normalize_row(r) for r in cur.fetchall()]
    if not include_hidden:
        comments = [
            c
            for c in comments
            if c.get("review_status") != "hidden" or c.get("author_user_id") == viewer_user_id
        ]
    if exclude_user_ids:
        comments = [c for c in comments if c.get("author_user_id") not in exclude_user_ids]
    result = []
    for c in comments:
        item = dict(c)
        item.pop("computed_trust_score", None)
        is_own = viewer_user_id is not None and item.get("author_user_id") == viewer_user_id
        if not is_own:
            item["flagged_reason"] = None
        result.append(item)
    return result


def count_all_comments() -> int:
    """Total comments stored across every place, regardless of
    review_status (0 if the table is empty) - used by
    GET /moderation/stats in api/main.py."""
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM comments")
        row = cur.fetchone()
    return row["n"] if row else 0


def sum_helpful_by_place() -> dict[str, int]:
    """Sum of helpful_count across all *visible* comments, grouped by
    place_id - used by GET /places/popularity-scores (api/main.py) as part
    of the venue popularity signal (see checkins_store.sum_helpful_status_by_place
    for the same pattern applied to status updates). Hidden/flagged
    comments are excluded - content nobody actually saw shouldn't count
    toward a venue's popularity."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT place_id, SUM(helpful_count) AS total
            FROM comments
            WHERE review_status != 'hidden'
            GROUP BY place_id
            HAVING SUM(helpful_count) > 0
            """
        )
        rows = cur.fetchall()
    return {row["place_id"]: row["total"] for row in rows}


def list_place_ids_with_comments() -> set[str]:
    """place_ids with at least one comment (any review_status) - used to
    compute GET /moderation/stats venues_with_activity in api/main.py
    (unioned there with checkins_store.list_place_ids_with_activity)."""
    with get_cursor() as cur:
        cur.execute("SELECT DISTINCT place_id FROM comments")
        rows = cur.fetchall()
    return {row["place_id"] for row in rows}


def list_hidden_comments() -> list[dict]:
    """Every comment across every place that's hidden or flagged -
    moderator-only visibility (see api/main.py get_current_moderator)."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT * FROM comments
            WHERE review_status = 'hidden' OR flagged_reason IS NOT NULL
            ORDER BY created_at
            """
        )
        rows = cur.fetchall()
    return [_normalize_row(r) for r in rows]


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

    `SELECT ... FOR UPDATE` locks the row for the rest of this transaction,
    so two concurrent toggles from different users can't both read the same
    helpful_user_ids and race each other's UPDATE.
    """
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM comments WHERE place_id = %s AND id = %s FOR UPDATE",
            (place_id, comment_id),
        )
        row = cur.fetchone()
        if row is None:
            raise CommentError("Yorum bulunamadı.")
        if row.get("author_user_id") == user_id:
            raise SelfHelpfulError("Kendi yorumunu faydalı olarak işaretleyemezsin.")
        helpful_ids = list(row.get("helpful_user_ids") or [])
        if user_id in helpful_ids:
            helpful_ids.remove(user_id)
        else:
            helpful_ids.append(user_id)
        cur.execute(
            """
            UPDATE comments SET helpful_user_ids = %s, helpful_count = %s
            WHERE place_id = %s AND id = %s
            RETURNING *
            """,
            (helpful_ids, len(helpful_ids), place_id, comment_id),
        )
        updated = cur.fetchone()
    if updated is None:
        raise RuntimeError("UPDATE ... RETURNING satır döndürmedi (beklenmeyen durum).")
    return _normalize_row(updated)


def restore_comment(comment_id: str) -> dict:
    """Moderator override: set a comment's review_status back to "visible"
    (e.g. the content filter false-positived). Raises CommentError if no
    comment with this id exists."""
    with get_cursor() as cur:
        cur.execute(
            """
            UPDATE comments SET review_status = 'visible', flagged_reason = NULL
            WHERE id = %s
            RETURNING *
            """,
            (comment_id,),
        )
        row = cur.fetchone()
    if row is None:
        raise CommentError("Yorum bulunamadı.")
    return _normalize_row(row)
