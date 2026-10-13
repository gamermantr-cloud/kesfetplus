"""PostgreSQL-backed content report storage.

Used to be a JSON file (database/reports.json) guarded by a
threading.Lock - see database/README.md and git history for that version.
Now backed by the `reports` table (database/schema.sql). As before, a
report is *recorded*, never auto-deletes the reported content - see
docs/research/app-store-yayinlama-yol-haritasi.md ("1.2 UGC"). Automatic
removal without a human moderator looking at it is deliberately not
implemented.

Every public function here keeps the exact same name/signature/return
shape it had as a JSON store, so api/main.py needed no changes at all.
"""

from __future__ import annotations

import html
import uuid
from datetime import UTC, datetime

from database.db import get_cursor

VALID_TARGET_TYPES = ("comment", "status", "checkin")


class ReportError(Exception):
    """Raised when a report lookup (e.g. resolve) doesn't match a real id."""


def add_report(
    reporter_user_id: str,
    target_type: str,
    target_id: str,
    place_id: str,
    reason: str,
) -> dict:
    report_id = str(uuid.uuid4())
    created_at = datetime.now(UTC)
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO reports (
                id, reporter_user_id, target_type, target_id, place_id,
                reason, created_at, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'open')
            RETURNING *
            """,
            (
                report_id,
                reporter_user_id,
                target_type,
                target_id,
                place_id,
                html.escape(reason),
                created_at,
            ),
        )
        row = cur.fetchone()
    if row is None:
        raise RuntimeError("INSERT ... RETURNING satır döndürmedi (beklenmeyen durum).")
    return dict(row)


def list_reports_by_user(reporter_user_id: str) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM reports WHERE reporter_user_id = %s ORDER BY created_at",
            (reporter_user_id,),
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def list_all_reports() -> list[dict]:
    """Every report from every user - moderator-only (see
    api/main.py get_current_moderator)."""
    with get_cursor() as cur:
        cur.execute("SELECT * FROM reports ORDER BY created_at")
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def resolve_report(report_id: str) -> dict:
    """Mark a report as reviewed by a moderator. Never touches the reported
    content itself - see module docstring. Raises ReportError if no report
    with this id exists."""
    with get_cursor() as cur:
        cur.execute(
            "UPDATE reports SET status = 'resolved' WHERE id = %s RETURNING *",
            (report_id,),
        )
        row = cur.fetchone()
    if row is None:
        raise ReportError("Şikayet bulunamadı.")
    return dict(row)
