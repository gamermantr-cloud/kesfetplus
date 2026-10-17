"""PostgreSQL-backed user account, session, and block-list storage.

Used to be two JSON files (users.json, sessions.json) guarded by a
threading.Lock - see database/README.md and git history for that version.
Now backed by the `users` and `sessions` tables (database/schema.sql);
every write runs inside one DB transaction via database/db.get_cursor(),
which is what replaces the old lock (and, unlike it, stays correct across
multiple worker processes too).

Columns on `users`: id, email, password_hash, display_name, created_at,
blocked_user_ids, is_moderator, referral_code, referred_by, member_number,
is_founding_member - the exact same fields the JSON record used to have.
`sessions`: token (PK), user_id, created_at.

Passwords are hashed with bcrypt - never stored or returned in plaintext.
_public_user() strips password_hash before a user dict is ever handed back
to a caller (API response, etc.).

Sessions are plain random tokens, not JWT - see the version of this
docstring in git history for the original reasoning (this project had no
other auth/crypto dependency); that reasoning doesn't change just because
the storage moved from a JSON file to a `sessions` table - it's still a
trivial `DELETE FROM sessions WHERE token = ...` for logout/revocation,
still no signing secret or expiry handling to build.

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
1-indexed registration order - "3. Kurucu Üye" etc.). member_number now
comes from the `member_number_seq` DB sequence (database/schema.sql)
instead of `len(users) + 1` under a Python lock - a sequence gives the
same "real, atomic, monotonically increasing registration order"
guarantee, but actually holds under concurrent registrations from
multiple API workers, which a single-process threading.Lock never did.
is_founding_member is a fixed snapshot taken *at* registration - it is
deliberately never recalculated afterward, unlike count_referrals() below.

Every account also gets a unique, short referral_code generated at
registration (see _generate_referral_code) and an optional referred_by
(the user_id of whoever's code they registered with, or None). Per the
research report's manipulation-risk warning, referred_by never feeds
trust-scoring or any other weighted metric - the only thing built on top
of it is a plain, honest count (count_referrals): "how many accounts have
referred_by == this user's id", counted fresh from the table every call,
same never-stored-always-recomputed pattern as count_user_statuses() in
checkins_store.py.

Every public function here keeps the exact same name/signature/return
shape it had as a JSON store, so api/main.py needed no changes at all.
"""

from __future__ import annotations

import os
import re
import secrets
import string
import uuid
from datetime import UTC, datetime
from typing import Any

import bcrypt
from dotenv import load_dotenv
from psycopg.errors import UniqueViolation

from database.db import get_cursor

load_dotenv()

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8

# First N registered accounts get is_founding_member=True. See module
# docstring "FOUNDING MEMBER / REFERRAL" note.
FOUNDING_MEMBER_LIMIT = 100

_REFERRAL_CODE_LENGTH = 6
_REFERRAL_CODE_ALPHABET = string.ascii_uppercase + string.digits


class UserError(Exception):
    """User-facing auth error (bad input, duplicate email, wrong password)."""


def _public_user(user: dict[str, Any]) -> dict[str, Any]:
    """User dict without password_hash - safe to return over the API."""
    return {k: v for k, v in user.items() if k != "password_hash"}


def _moderator_emails() -> set[str]:
    """MODERATOR_EMAILS env var - comma-separated, case-insensitive. See
    module docstring "MODERATION MVP" note."""
    raw = os.getenv("MODERATOR_EMAILS", "")
    return {email.strip().lower() for email in raw.split(",") if email.strip()}


def _sync_moderator_status(user: dict[str, Any]) -> dict[str, Any]:
    """Recompute is_moderator from MODERATOR_EMAILS and persist it if it
    changed, so editing the env var takes effect on the user's next
    login/token lookup without needing a fresh registration."""
    should_be_moderator = user["email"] in _moderator_emails()
    if user.get("is_moderator", False) == should_be_moderator:
        return user
    with get_cursor() as cur:
        cur.execute(
            "UPDATE users SET is_moderator = %s WHERE id = %s",
            (should_be_moderator, user["id"]),
        )
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
    code already in the table (existing_codes - passed in so this stays
    callable with a single query result instead of re-querying here)."""
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
    None) - a bad/typo'd invite code should never block registration.

    The proactive `SELECT ... WHERE email = %s` duplicate check below is
    not airtight against a *concurrent* registration of the same email (a
    second request could pass it before the first commits) - the `users.email`
    UNIQUE constraint is the real guarantee, and a UniqueViolation on the
    final INSERT is caught and turned into the same UserError, so the
    proactive check only exists to give the common (non-racing) case a
    clean error message without round-tripping through a DB exception.
    """
    email = email.strip().lower()
    if not _EMAIL_RE.match(email):
        raise UserError("Geçersiz e-posta adresi.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise UserError(f"Şifre en az {MIN_PASSWORD_LENGTH} karakter olmalı.")
    display_name = display_name.strip()
    if not display_name:
        raise UserError("Görünen isim boş olamaz.")

    normalized_ref_code = referral_code.strip().upper() if referral_code else None

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user_id = str(uuid.uuid4())

    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE email = %s", (email,))
            if cur.fetchone() is not None:
                raise UserError("Bu e-posta zaten kayıtlı.")

            cur.execute("SELECT referral_code FROM users")
            existing_codes = {row["referral_code"] for row in cur.fetchall()}
            new_referral_code = _generate_referral_code(display_name, existing_codes)

            referred_by = None
            if normalized_ref_code:
                cur.execute(
                    "SELECT id FROM users WHERE referral_code = %s",
                    (normalized_ref_code,),
                )
                match = cur.fetchone()
                if match is not None:
                    referred_by = match["id"]

            cur.execute("SELECT nextval('member_number_seq') AS n")
            seq_row = cur.fetchone()
            if seq_row is None:
                raise RuntimeError("nextval('member_number_seq') satır döndürmedi.")
            member_number = seq_row["n"]
            is_founding_member = member_number <= FOUNDING_MEMBER_LIMIT

            created_at = datetime.now(UTC)
            cur.execute(
                """
                INSERT INTO users (
                    id, email, password_hash, display_name, created_at,
                    blocked_user_ids, is_moderator, referral_code, referred_by,
                    member_number, is_founding_member
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    user_id,
                    email,
                    password_hash,
                    display_name,
                    created_at,
                    [],
                    email in _moderator_emails(),
                    new_referral_code,
                    referred_by,
                    member_number,
                    is_founding_member,
                ),
            )
            row = cur.fetchone()
    except UniqueViolation as e:
        raise UserError("Bu e-posta zaten kayıtlı.") from e
    if row is None:
        raise RuntimeError("INSERT ... RETURNING satır döndürmedi (beklenmeyen durum).")
    return _public_user(dict(row))


def authenticate(email: str, password: str) -> dict:
    """Verify email+password. Raises UserError on any mismatch (no user
    enumeration - same message whether the email exists or not)."""
    email = email.strip().lower()
    with get_cursor() as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
    if row is not None and bcrypt.checkpw(
        password.encode("utf-8"), row["password_hash"].encode("utf-8")
    ):
        return _public_user(_sync_moderator_status(dict(row)))
    raise UserError("E-posta veya şifre hatalı.")


def count_users() -> int:
    """Total registered accounts (0 if the table is empty) - used by
    GET /moderation/stats in api/main.py."""
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM users")
        row = cur.fetchone()
    return row["n"] if row else 0


def count_referrals(user_id: str) -> int:
    """How many accounts have referred_by == user_id - real count, computed
    fresh from the table every call, never stored. See module docstring
    "FOUNDING MEMBER / REFERRAL" note for why this is deliberately just a
    plain visible count, not a trust-score input."""
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM users WHERE referred_by = %s", (user_id,))
        row = cur.fetchone()
    return row["n"] if row else 0


def get_user_by_id(user_id: str) -> dict | None:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
    if row is None:
        return None
    return _public_user(_sync_moderator_status(dict(row)))


def get_public_profile(user_id: str) -> dict | None:
    """Minimal, safe-for-anyone-to-see profile (no email) - used to show a
    display name for e.g. an entry in someone else's blocked_user_ids list."""
    user = get_user_by_id(user_id)
    if not user:
        return None
    return {"id": user["id"], "display_name": user["display_name"]}


def create_session(user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO sessions (token, user_id, created_at) VALUES (%s, %s, %s)",
            (token, user_id, datetime.now(UTC)),
        )
    return token


def get_user_by_token(token: str) -> dict | None:
    with get_cursor() as cur:
        cur.execute("SELECT user_id FROM sessions WHERE token = %s", (token,))
        session = cur.fetchone()
    if not session:
        return None
    return get_user_by_id(session["user_id"])


def delete_session(token: str) -> None:
    with get_cursor() as cur:
        cur.execute("DELETE FROM sessions WHERE token = %s", (token,))


def delete_user(user_id: str, password: str) -> None:
    """Permanently delete an account (App Store Guideline 5.1.1(v): the app
    must offer in-app account deletion). Raises UserError if the account
    doesn't exist or the password doesn't match - re-authentication is
    required before a destructive, irreversible action like this.

    The `users` row is the single source of truth every other table's
    FK points back to (database/schema.sql), so one DELETE here is enough:
    - sessions / push_subscriptions / reports (reporter_user_id): ON DELETE
      CASCADE - gone automatically, nothing left to act on them with.
    - comments / checkins / status_updates (author_user_id): ON DELETE SET
      NULL - the *content* is kept (it already carries its own copied
      `author` display-name string, same as a deleted Reddit/HN account
      shows old posts under "[deleted]"'s author field, not literally wiped
      - and other users may have already read/relied on it), only the link
      back to this now-gone account is cleared. This also matches the
      project's own anti-manipulation stance (see users_store.py module
      docstring "FOUNDING MEMBER / REFERRAL"): content is real, submitted
      data, never retroactively invalidated just because its author later
      deleted their account.
    - users.referred_by (other users who registered with this one's invite
      code): ON DELETE SET NULL - their own count_referrals() unaffected,
      they just stop pointing at a referrer that no longer exists.
    """
    with get_cursor() as cur:
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        if row is None:
            raise UserError("Kullanıcı bulunamadı.")
        if not bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8")):
            raise UserError("Şifre hatalı.")
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))


def set_blocked(user_id: str, target_user_id: str, blocked: bool) -> list[str]:
    """Add/remove target_user_id from user_id's blocked_user_ids. Returns the
    updated list. Raises UserError if user_id doesn't exist or targets self.

    `SELECT ... FOR UPDATE` locks the row for the rest of this transaction,
    so two concurrent block/unblock calls for the same user can't race each
    other's read-modify-write of blocked_user_ids."""
    if target_user_id == user_id:
        raise UserError("Kendini engelleyemezsin.")
    with get_cursor() as cur:
        cur.execute("SELECT blocked_user_ids FROM users WHERE id = %s FOR UPDATE", (user_id,))
        row = cur.fetchone()
        if row is None:
            raise UserError("Kullanıcı bulunamadı.")
        blocked_ids = set(row.get("blocked_user_ids") or [])
        if blocked:
            blocked_ids.add(target_user_id)
        else:
            blocked_ids.discard(target_user_id)
        new_blocked_ids = sorted(blocked_ids)
        cur.execute(
            "UPDATE users SET blocked_user_ids = %s WHERE id = %s",
            (new_blocked_ids, user_id),
        )
    return new_blocked_ids
