"""File-backed Web Push subscription storage.

Same pattern as users_store.py / checkins_store.py: temporary until
PostgreSQL is wired up. One JSON file:

- push_subscriptions.json -> user_id -> list of subscription dicts, each
  `{endpoint, keys: {p256dh, auth}, created_at}` - exactly the shape the
  browser's PushSubscription.toJSON() produces (see
  frontend/src/lib/push.js), so no reshaping happens on the way in.

A user can have more than one subscription (e.g. phone + laptop), so this
stores a list per user_id rather than a single object. Subscribing again
with the same endpoint replaces the old entry instead of duplicating it
(a browser occasionally rotates the endpoint on the same install, and the
old one would otherwise linger as a dead entry that always 410s).

KNOWN LIMITATION: same as every other store here - the threading.Lock only
guards a single process; not safe for `uvicorn --workers N`.
"""

import json
import os
import threading
from datetime import UTC, datetime

_STORE_PATH = os.path.join(os.path.dirname(__file__), "push_subscriptions.json")
_lock = threading.Lock()


def _load() -> dict:
    if not os.path.exists(_STORE_PATH):
        return {}
    with open(_STORE_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict) -> None:
    with open(_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_subscription(user_id: str, endpoint: str, p256dh: str, auth: str) -> dict:
    """Save (or replace, if the endpoint is already known for this user) a
    push subscription for user_id."""
    subscription = {
        "endpoint": endpoint,
        "keys": {"p256dh": p256dh, "auth": auth},
        "created_at": datetime.now(UTC).isoformat(),
    }
    with _lock:
        data = _load()
        subs = [s for s in data.get(user_id, []) if s["endpoint"] != endpoint]
        subs.append(subscription)
        data[user_id] = subs
        _save(data)
    return subscription


def remove_subscription(user_id: str, endpoint: str) -> None:
    """Remove one subscription by endpoint. No error if it isn't found -
    unsubscribing something already gone is a no-op, not a failure."""
    with _lock:
        data = _load()
        subs = data.get(user_id)
        if not subs:
            return
        data[user_id] = [s for s in subs if s["endpoint"] != endpoint]
        _save(data)


def remove_subscription_by_endpoint(endpoint: str) -> None:
    """Remove a subscription by endpoint alone, regardless of which user it
    belongs to. Used when a push send comes back 410 Gone/404 (the push
    service itself says the subscription is dead) - see
    database/push_notify.py."""
    with _lock:
        data = _load()
        changed = False
        for user_id, subs in list(data.items()):
            kept = [s for s in subs if s["endpoint"] != endpoint]
            if len(kept) != len(subs):
                data[user_id] = kept
                changed = True
        if changed:
            _save(data)


def list_subscriptions(user_id: str) -> list[dict]:
    with _lock:
        data = _load()
    return data.get(user_id, [])


def list_subscriptions_for_users(user_ids: set[str]) -> dict[str, list[dict]]:
    """user_id -> its subscriptions, for a batch of users at once - used by
    the check-in-based notify fan-out in checkins_store.add_status so it
    only reads the JSON file once instead of once per recipient."""
    with _lock:
        data = _load()
    return {uid: data[uid] for uid in user_ids if data.get(uid)}
