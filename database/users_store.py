"""File-backed user account, session, and block-list storage.

Same pattern as comments_store.py: temporary until PostgreSQL is wired up.
Two JSON files:

- users.json    -> user_id -> {id, email, password_hash, display_name,
                    created_at, blocked_user_ids}
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
"""

from __future__ import annotations

import json
import os
import re
import secrets
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


def register_user(email: str, password: str, display_name: str) -> dict:
    """Create a new account. Raises UserError on bad input or duplicate email."""
    email = email.strip().lower()
    if not _EMAIL_RE.match(email):
        raise UserError("Geçersiz e-posta adresi.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise UserError(f"Şifre en az {MIN_PASSWORD_LENGTH} karakter olmalı.")
    display_name = display_name.strip()
    if not display_name:
        raise UserError("Görünen isim boş olamaz.")

    with _lock:
        users = _load(_USERS_PATH)
        if any(u["email"] == email for u in users.values()):
            raise UserError("Bu e-posta zaten kayıtlı.")
        user_id = str(uuid.uuid4())
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user = {
            "id": user_id,
            "email": email,
            "password_hash": password_hash,
            "display_name": display_name,
            "created_at": datetime.now(UTC).isoformat(),
            "blocked_user_ids": [],
            "is_moderator": email in _moderator_emails(),
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
