"""File-backed user account, session, and block-list storage.

Same pattern as comments_store.py: temporary until PostgreSQL is wired up.
Two JSON files:

- users.json    -> user_id -> {id, email, password_hash, display_name,
                    created_at, blocked_user_ids, referral_code, referred_by,
                    member_number, is_founding_member}
- sessions.json -> opaque token -> {user_id, created_at}

Passwords are hashed with bcrypt - never stored or returned in plaintext.
_public_user() strips password_hash before a user dict is ever handed back
to a caller (API response, etc.).

Sessions are plain random tokens, not JWT. See docs/research (or the task
report that introduced this file) for the reasoning: this project already
uses file-backed JSON stores everywhere (comments_store.py,
checkins_store.py) with no other auth/crypto dependency, so an opaque
token + a sessions.json lookup matches that pattern exactly, needs no
extra library (stdlib `secrets` only), and makes logout/revocation a
trivial dict delete - a JWT would need a signing secret, expiry handling,
and *still* a revocation list to support real logout, which is strictly
more code for less benefit at this scale.

display_name is stored as the user typed it (trimmed, non-empty) -
*not* HTML-escaped here. It gets escaped downstream at the point it's
written into a comment/check-in/status record (comments_store.py /
checkins_store.py already html.escape() the `author` field) - escaping
it here too would double-escape it (e.g. "&" -> "&amp;" -> "&amp;amp;").
API responses that include display_name raw (e.g. /auth/me) are fine
because the frontend renders them through React, which escapes on render.

MODERATION MVP: there's no role-management UI. The *only* way to become a
moderator is to be listed in the MODERATOR_EMAILS env var (comma-separated
email list, read via `.env` - see .env.example). is_moderator is computed
from that list at register time and re-synced on every login/token lookup
(_sync_moderator_status), so adding/removing an email from the env var
takes effect the next time that user authenticates - no need to re-register.
This is deliberately minimal (see api/main.py's moderation endpoints for
what a moderator can actually do); a real admin UI is out of scope.

FOUNDING MEMBER / REFERRAL (see docs/research/buyume-ilk-100-kullanici-
stratejisi.md, Bölüm 1.4 & 2.4): the first 100 registered accounts get
is_founding_member=True plus the real, stored member_number (their
1-indexed registration order - "3. Kurucu Üye" etc.) so the number can be
shown later without recomputing registration order from created_at.
is_founding_member is a fixed snapshot taken *at* registration (based on
how many accounts already existed at that moment, under the same lock as
the insert itself, so no race with a concurrent registration) - it is
deliberately never recalculated afterward, unlike count_referrals() below.

Every account also gets a unique, short referral_code generated at
registration (see _generate_referral_code) and an optional referred_by
(the user_id of whoever's code they registered with, or None). Per the
research report's manipulation-risk warning, referred_by never feeds
trust-scoring or any other weighted metric - the only thing built on top
of it is a plain, honest count (count_referrals): "how many accounts have
referred_by == this user's id", counted fresh from users.json every call,
same never-stored-always-recomputed pattern as count_user_statuses() in
checkins_store.py.
"""

from __future__ import annotations

import json
import os
import re
import secrets
import string
import threading
import uuid
from datetime import UTC, datetime

import bcrypt
from dotenv import load_dotenv

load_dotenv()

_USERS_PATH = os.path.join(os.path.dirname(__file__), "users.json")
_SESSIONS_PATH = os.path.join(os.path.dirname(__file__), "sessions.json")
_lock = threading.Lock()

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8

# First N registered accounts get is_founding_member=True. See module
# docstring "FOUNDING MEMBER / REFERRAL" note.
FOUNDING_MEMBER_LIMIT = 100

_REFERRAL_CODE_LENGTH = 6
_REFERRAL_CODE_ALPHABET = string.ascii_uppercase + string.digits


class UserError(Exception):
    """User-facing auth error (bad input, duplicate email, wrong password)."""


def _load(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _public_user(user: dict) -> dict:
    """User dict without password_hash - safe to return over the API."""
    return {k: v for k, v in user.items() if k != "password_hash"}


def _moderator_emails() -> set[str]:
    """MODERATOR_EMAILS env var - comma-separated, case-insensitive. See
    module docstring "MODERATION MVP" note."""
    raw = os.getenv("MODERATOR_EMAILS", "")
    return {email.strip().lower() for email in raw.split(",") if email.strip()}


def _sync_moderator_status(user: dict) -> dict:
    """Recompute is_moderator from MODERATOR_EMAILS and persist it if it
    changed, so editing the env var takes effect on the user's next
    login/token lookup without needing a fresh registration. Also backfills
    the field for accounts created before this field existed."""
    should_be_moderator = user["email"] in _moderator_emails()
    if user.get("is_moderator", False) == should_be_moderator:
        user.setdefault("is_moderator", should_be_moderator)
        return user
    with _lock:
        users = _load(_USERS_PATH)
        stored = users.get(user["id"])
        if stored is not None:
            stored["is_moderator"] = should_be_moderator
            users[user["id"]] = stored
            _save(_USERS_PATH, users)
    return {**user, "is_moderator": should_be_moderator}


def _referral_code_prefix(display_name: str) -> str:
    """Up to 4 uppercase alnum chars derived from display_name, so a code
    stays loosely recognizable (e.g. "Ayse Kaya" -> "AYSE"). Non-ASCII
    letters (ç, ş, ğ, ı, ö, ü, or any other script) are simply dropped -
    the random suffix in _generate_referral_code still fills the code out
    to a valid, unique one even if this returns "" (e.g. an all-Arabic or
    all-Cyrillic display_name)."""
    ascii_alnum = [ch for ch in display_name.upper() if ch in _REFERRAL_CODE_ALPHABET]
    return "".join(ascii_alnum[:4])


def _generate_referral_code(display_name: str, existing_codes: set[str]) -> str:
    """Unique _REFERRAL_CODE_LENGTH-char referral code: a display_name-derived
    prefix padded with random chars, retried on collision against every
    code already in users.json (existing_codes - passed in so this stays
    callable under the same lock that's already holding the loaded users
    dict, instead of re-reading the file here)."""
    prefix = _referral_code_prefix(display_name)
    for _ in range(50):
        pad_len = _REFERRAL_CODE_LENGTH - len(prefix)
        suffix = "".join(secrets.choice(_REFERRAL_CODE_ALPHABET) for _ in range(pad_len))
        code = prefix + suffix
        if code not in existing_codes:
            return code
    # Astronomically unlikely fallback if 50 collisions happen in a row:
    # a longer fully-random code, still checked for uniqueness.
    fallback_length = _REFERRAL_CODE_LENGTH + 4
    while True:
        code = "".join(secrets.choice(_REFERRAL_CODE_ALPHABET) for _ in range(fallback_length))
        if code not in existing_codes:
            return code


def register_user(
    email: str, password: str, display_name: str, referral_code: str | None = None
) -> dict:
    """Create a new account. Raises UserError on bad input or duplicate email.

    referral_code (optional): the *inviter's* referral code, as typed/passed
    by the new user (e.g. from a `?ref=` link). If it matches an existing
    account's referral_code, that account's id is stored as referred_by. An
    unrecognized or missing code is silently ignored (referred_by stays
    None) - a bad/typo'd invite code should never block registration."""
    email = email.strip().lower()
    if not _EMAIL_RE.match(email):
        raise UserError("Geçersiz e-posta adresi.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise UserError(f"Şifre en az {MIN_PASSWORD_LENGTH} karakter olmalı.")
    display_name = display_name.strip()
    if not display_name:
        raise UserError("Görünen isim boş olamaz.")

    normalized_ref_code = referral_code.strip().upper() if referral_code else None

    with _lock:
        users = _load(_USERS_PATH)
        if any(u["email"] == email for u in users.values()):
            raise UserError("Bu e-posta zaten kayıtlı.")
        user_id = str(uuid.uuid4())
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Real registration-order count, taken under this same lock (so it
        # can't race with a concurrent registration) - NOT a call to the
        # module-level count_users(), which takes _lock itself and would
        # deadlock (plain threading.Lock, not reentrant) if called from in
        # here. len(users) before insertion is exactly what count_users()
        # would have returned at this instant anyway.
        member_number = len(users) + 1
        is_founding_member = member_number <= FOUNDING_MEMBER_LIMIT

        existing_codes = {u["referral_code"] for u in users.values() if u.get("referral_code")}
        new_referral_code = _generate_referral_code(display_name, existing_codes)

        referred_by = None
        if normalized_ref_code:
            for candidate in users.values():
                if candidate.get("referral_code") == normalized_ref_code:
                    referred_by = candidate["id"]
                    break

        user: dict = {
            "id": user_id,
            "email": email,
            "password_hash": password_hash,
            "display_name": display_name,
            "created_at": datetime.now(UTC).isoformat(),
            "blocked_user_ids": [],
            "is_moderator": email in _moderator_emails(),
            "referral_code": new_referral_code,
            "referred_by": referred_by,
            "member_number": member_number,
            "is_founding_member": is_founding_member,
        }
        users[user_id] = user
        _save(_USERS_PATH, users)
    return _public_user(user)


def authenticate(email: str, password: str) -> dict:
    """Verify email+password. Raises UserError on any mismatch (no user
    enumeration - same message whether the email exists or not)."""
    email = email.strip().lower()
    with _lock:
        users = _load(_USERS_PATH)
    for user in users.values():
        if user["email"] == email:
            if bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
                return _public_user(_sync_moderator_status(user))
            break
    raise UserError("E-posta veya şifre hatalı.")


def count_users() -> int:
    """Total registered accounts (real count from users.json, 0 if the file
    is missing/empty) - used by GET /moderation/stats in api/main.py."""
    with _lock:
        users = _load(_USERS_PATH)
    return len(users)


def count_referrals(user_id: str) -> int:
    """How many accounts have referred_by == user_id - real count, computed
    fresh from users.json every call, never stored. See module docstring
    "FOUNDING MEMBER / REFERRAL" note for why this is deliberately just a
    plain visible count, not a trust-score input."""
    with _lock:
        users = _load(_USERS_PATH)
    return sum(1 for u in users.values() if u.get("referred_by") == user_id)


def get_user_by_id(user_id: str) -> dict | None:
    with _lock:
        users = _load(_USERS_PATH)
    user = users.get(user_id)
    return _public_user(_sync_moderator_status(user)) if user else None


def get_public_profile(user_id: str) -> dict | None:
    """Minimal, safe-for-anyone-to-see profile (no email) - used to show a
    display name for e.g. an entry in someone else's blocked_user_ids list."""
    user = get_user_by_id(user_id)
    if not user:
        return None
    return {"id": user["id"], "display_name": user["display_name"]}


def create_session(user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    with _lock:
        sessions = _load(_SESSIONS_PATH)
        sessions[token] = {
            "user_id": user_id,
            "created_at": datetime.now(UTC).isoformat(),
        }
        _save(_SESSIONS_PATH, sessions)
    return token


def get_user_by_token(token: str) -> dict | None:
    with _lock:
        sessions = _load(_SESSIONS_PATH)
    session = sessions.get(token)
    if not session:
        return None
    return get_user_by_id(session["user_id"])


def delete_session(token: str) -> None:
    with _lock:
        sessions = _load(_SESSIONS_PATH)
        if token in sessions:
            del sessions[token]
            _save(_SESSIONS_PATH, sessions)


def set_blocked(user_id: str, target_user_id: str, blocked: bool) -> list[str]:
    """Add/remove target_user_id from user_id's blocked_user_ids. Returns the
    updated list. Raises UserError if user_id doesn't exist or targets self."""
    if target_user_id == user_id:
        raise UserError("Kendini engelleyemezsin.")
    with _lock:
        users = _load(_USERS_PATH)
        user = users.get(user_id)
        if not user:
            raise UserError("Kullanıcı bulunamadı.")
        blocked_ids = set(user.get("blocked_user_ids", []))
        if blocked:
            blocked_ids.add(target_user_id)
        else:
            blocked_ids.discard(target_user_id)
        user["blocked_user_ids"] = sorted(blocked_ids)
        users[user_id] = user
        _save(_USERS_PATH, users)
    return user["blocked_user_ids"]
