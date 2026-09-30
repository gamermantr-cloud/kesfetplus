"""File-backed content report storage.

Same pattern as comments_store.py: temporary until PostgreSQL is wired up.
Reports are appended to reports.json for later human review - see
docs/research/app-store-yayinlama-yol-haritasi.md ("1.2 UGC"): a report is
*recorded*, never auto-deletes the reported content. Automatic removal
without a human moderator looking at it is deliberately not implemented.
"""

import html
import json
import os
import threading
import uuid
from datetime import UTC, datetime

_STORE_PATH = os.path.join(os.path.dirname(__file__), "reports.json")
_lock = threading.Lock()

VALID_TARGET_TYPES = ("comment", "status", "checkin")


class ReportError(Exception):
    """Raised when a report lookup (e.g. resolve) doesn't match a real id."""


def _load() -> list[dict]:
    if not os.path.exists(_STORE_PATH):
        return []
    with open(_STORE_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save(data: list[dict]) -> None:
    with open(_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_report(
    reporter_user_id: str,
    target_type: str,
    target_id: str,
    place_id: str,
    reason: str,
) -> dict:
    report = {
        "id": str(uuid.uuid4()),
        "reporter_user_id": reporter_user_id,
        "target_type": target_type,
        "target_id": target_id,
        "place_id": place_id,
        "reason": html.escape(reason),
        "created_at": datetime.now(UTC).isoformat(),
        "status": "open",
    }
    with _lock:
        data = _load()
        data.append(report)
        _save(data)
    return report


def list_reports_by_user(reporter_user_id: str) -> list[dict]:
    with _lock:
        data = _load()
    return [r for r in data if r["reporter_user_id"] == reporter_user_id]


def list_all_reports() -> list[dict]:
    """Every report from every user - moderator-only (see
    api/main.py get_current_moderator)."""
    with _lock:
        return _load()


def resolve_report(report_id: str) -> dict:
    """Mark a report as reviewed by a moderator. Never touches the reported
    content itself - see module docstring. Raises ReportError if no report
    with this id exists."""
    with _lock:
        data = _load()
        for report in data:
            if report["id"] == report_id:
                report["status"] = "resolved"
                _save(data)
                return report
    raise ReportError("Şikayet bulunamadı.")
