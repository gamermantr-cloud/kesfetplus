"""PostgreSQL-backed Web Push subscription storage.

Used to be a JSON file (database/push_subscriptions.json) guarded by a
threading.Lock - see database/README.md and git history for that version.
Now backed by the `push_subscriptions` table (database/schema.sql), with
composite primary key (user_id, endpoint):

- A user can have more than one subscription (e.g. phone + laptop), so a
  user_id maps to several rows rather than one.
- Subscribing again with the same endpoint for the same user replaces the
  old row (`INSERT ... ON CONFLICT (user_id, endpoint) DO UPDATE`) instead
  of duplicating it - a browser occasionally rotates the endpoint on the
  same install, and the old one would otherwise linger as a dead entry that
  always 410s.

Every public function here keeps the exact same name/signature/return
shape it had as a JSON store, so api/main.py needed no changes at all.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from database.db import get_cursor


def _row_to_subscription(row: dict[str, Any]) -> dict[str, Any]:
    """DB row (flat p256dh/auth columns) -> the nested shape the JSON store
    used to produce - exactly what the browser's PushSubscription.toJSON()
    produces (see frontend/src/lib/push.js), so no reshaping happens on the
    way back out either."""
    created_at = row["created_at"]
    return {
        "endpoint": row["endpoint"],
        "keys": {"p256dh": row["p256dh"], "auth": row["auth"]},
        "created_at": created_at.isoformat() if isinstance(created_at, datetime) else created_at,
    }


def add_subscription(user_id: str, endpoint: str, p256dh: str, auth: str) -> dict:
    """Save (or replace, if the endpoint is already known for this user) a
    push subscription for user_id."""
    created_at = datetime.now(UTC)
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO push_subscriptions (user_id, endpoint, p256dh, auth, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id, endpoint)
            DO UPDATE SET p256dh = EXCLUDED.p256dh, auth = EXCLUDED.auth,
                          created_at = EXCLUDED.created_at
            RETURNING *
            """,
            (user_id, endpoint, p256dh, auth, created_at),
        )
        row = cur.fetchone()
    if row is None:
        raise RuntimeError("UPSERT ... RETURNING satır döndürmedi (beklenmeyen durum).")
    return _row_to_subscription(row)


def remove_subscription(user_id: str, endpoint: str) -> None:
    """Remove one subscription by endpoint. No error if it isn't found -
    unsubscribing something already gone is a no-op, not a failure."""
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM push_subscriptions WHERE user_id = %s AND endpoint = %s",
            (user_id, endpoint),
        )


def remove_subscription_by_endpoint(endpoint: str) -> None:
    """Remove a subscription by endpoint alone, regardless of which user it
    belongs to. Used when a push send comes back 410 Gone/404 (the push
    service itself says the subscription is dead) - see
    database/push_notify.py."""
    with get_cursor() as cur:
        cur.execute("DELETE FROM push_subscriptions WHERE endpoint = %s", (endpoint,))


def list_subscriptions(user_id: str) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM push_subscriptions WHERE user_id = %s ORDER BY created_at",
            (user_id,),
        )
        rows = cur.fetchall()
    return [_row_to_subscription(r) for r in rows]


def list_subscriptions_for_users(user_ids: set[str]) -> dict[str, list[dict]]:
    """user_id -> its subscriptions, for a batch of users at once - used by
    the check-in-based notify fan-out in checkins_store.add_status so it
    only queries once instead of once per recipient."""
    if not user_ids:
        return {}
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM push_subscriptions WHERE user_id = ANY(%s) ORDER BY created_at",
            (list(user_ids),),
        )
        rows = cur.fetchall()
    result: dict[str, list[dict]] = {}
    for row in rows:
        result.setdefault(row["user_id"], []).append(_row_to_subscription(row))
    return result
