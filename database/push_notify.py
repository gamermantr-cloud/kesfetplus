"""Real Web Push sending (RFC 8030 push protocol, via the `pywebpush`
library) - triggered by checkins_store.add_status when a new status update
is posted at a venue someone recently checked into.

See docs/research/sonraki-adimlar-firsat-analizi.md item 4 ("Push bildirim
altyapısı hâlâ yok") and CLAUDE.md's "sahte veri yasak" rule, which this
module is written to respect for *behavior*, not just data: there is no
fake/simulated "notification sent" anywhere here. Every call either
genuinely reaches pywebpush.webpush() - a real HTTPS POST to the browser
vendor's push service - or is skipped for an honest, logged reason (VAPID
keys not configured yet, no subscribers for this venue).

Sending a push must never be able to break the caller's actual job (saving
a status update). Every exception here is caught and logged, never raised -
see the module-level try/except wrapper in send_to_user_ids and the
per-subscription one in _send_one.
"""

import json
import logging
import os

from pywebpush import WebPushException, webpush

from database.push_subscriptions_store import (
    list_subscriptions_for_users,
    remove_subscription_by_endpoint,
)

logger = logging.getLogger(__name__)


def _vapid_config() -> tuple[str, str] | None:
    """Reads VAPID_PRIVATE_KEY / VAPID_CLAIMS_EMAIL from the environment
    (see .env.example and scripts/generate_vapid_keys.py). Returns None -
    never raises - if either is missing, so callers can skip honestly
    instead of crashing when a real deploy hasn't generated keys yet."""
    private_key = os.getenv("VAPID_PRIVATE_KEY")
    claims_email = os.getenv("VAPID_CLAIMS_EMAIL")
    if not private_key or not claims_email:
        return None
    return private_key, claims_email


def notify_new_status(
    place_id: str, venue_name: str, tag: str, recipient_user_ids: set[str]
) -> None:
    """Fan-out entry point called from checkins_store.add_status. Builds the
    notification payload and hands off to send_to_user_ids - see that
    function for the "never raises, never fakes a send" guarantee."""
    title = "Keşfet Plus"
    body = f"{venue_name} mekanında yeni bir durum paylaşıldı: {tag}"
    send_to_user_ids(recipient_user_ids, title, body, url=f"/place/{place_id}")


def send_to_user_ids(user_ids: set[str], title: str, body: str, url: str) -> None:
    """Best-effort real push send to every subscription belonging to
    user_ids. Never raises: every failure mode (no VAPID keys, no
    subscribers, a dead subscription, a network/library error) is caught
    here and logged, so a notification problem can never take down the
    request that triggered it (e.g. posting a status update)."""
    try:
        if not user_ids:
            return
        config = _vapid_config()
        if config is None:
            logger.info(
                "Push bildirimi atlandı: VAPID_PRIVATE_KEY/VAPID_CLAIMS_EMAIL "
                "henüz .env'de tanımlı değil (bkz. scripts/generate_vapid_keys.py)."
            )
            return
        private_key, claims_email = config

        subs_by_user = list_subscriptions_for_users(user_ids)
        if not subs_by_user:
            return

        payload = json.dumps({"title": title, "body": body, "url": url})
        for subs in subs_by_user.values():
            for sub in subs:
                _send_one(sub, payload, private_key, claims_email)
    except Exception:  # pragma: no cover - safety net, must never break add_status
        logger.exception("Push bildirimi gönderilirken beklenmeyen hata.")


def _send_one(subscription: dict, payload: str, private_key: str, claims_email: str) -> None:
    """Sends to exactly one subscription via a real pywebpush call. A
    404/410 response means the push service itself says the subscription is
    dead (browser uninstalled the app / cleared permission / the endpoint
    expired) - that's not an error, it's routine cleanup, so the
    subscription is quietly removed rather than logged as a failure.

    Catches Exception broadly (not just WebPushException) on purpose: a DNS
    failure or connection error for one bad/unreachable subscription (seen
    live in testing - requests.exceptions.ConnectionError escapes
    pywebpush's own WebPushException wrapping) must not abort the loop in
    send_to_user_ids and skip every *other* subscriber after it.
    """
    try:
        webpush(
            subscription_info=subscription,
            data=payload,
            vapid_private_key=private_key,
            vapid_claims={"sub": claims_email},
        )
    except WebPushException as e:
        status_code = getattr(e.response, "status_code", None)
        if status_code in (404, 410):
            remove_subscription_by_endpoint(subscription["endpoint"])
        else:
            logger.warning("Push gönderimi başarısız (HTTP %s): %s", status_code, e)
    except Exception:
        logger.exception(
            "Push gönderimi sırasında beklenmeyen hata (endpoint: %s).",
            subscription.get("endpoint"),
        )
