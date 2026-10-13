"""One-time migration: copies whatever real data is sitting in the old
JSON stores (database/{comments,checkins,status,users,sessions,reports,
push_subscriptions}.json - all gitignored, see .gitignore and
database/README.md) into the new PostgreSQL tables (database/schema.sql).

This is for real user data that may already exist on a machine that's been
running the file-based backend (comments people actually posted, accounts
people actually registered, etc.) - NOT for the venue catalog
(database/seed/*.json), which has its own script: scripts/seed_venues.py.

Idempotent / safe to re-run: every insert uses `ON CONFLICT ... DO NOTHING`
keyed on the row's original id (or natural key for push_subscriptions), so
running this twice against the same target database just no-ops the second
time instead of duplicating rows.

Order matters (foreign keys): users -> sessions/comments/checkins/
status_updates/reports/push_subscriptions, since all of those reference
users.id. Within `users`, some older records (see users_store.py's
docstring - accounts created before the founding-member/referral feature
existed) are missing referral_code/member_number/is_founding_member
entirely; this script backfills them the exact same way a fresh
registration would (database.users_store._generate_referral_code, and the
real `member_number_seq` DB sequence - see module docstring in
database/users_store.py) rather than inventing placeholder values.
referred_by needs a second pass: a user's inviter might appear later in
users.json's iteration order, so every user is first inserted with
referred_by=NULL, then a second pass fills in every referred_by that
points at an id that was actually migrated.

Usage (from the project root, with DATABASE_URL set in .env or the shell):
    venv\\Scripts\\python.exe scripts\\migrate_json_to_postgres.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from typing import Any

from dotenv import load_dotenv

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

load_dotenv()

from database.db import get_cursor  # noqa: E402
from database.users_store import (  # noqa: E402
    FOUNDING_MEMBER_LIMIT,
    _generate_referral_code,
    _moderator_emails,
)

_DB_DIR = os.path.join(_REPO_ROOT, "database")


def _load_json(filename: str, default: Any) -> Any:
    path = os.path.join(_DB_DIR, filename)
    if not os.path.exists(path):
        print(f"  {filename}: yok, atlanıyor (zaten boş kabul edilir).")
        return default
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data if data else default


def _parse_dt(value: str | None) -> datetime:
    if not value:
        return datetime.now(UTC)
    return datetime.fromisoformat(value)


def migrate_users() -> dict[str, str]:
    """Returns {old_user_id: email} for every user actually migrated (used
    only for a final summary; ids are kept identical, not remapped)."""
    print("\n1. users.json -> users")
    users: dict[str, dict] = _load_json("users.json", {})
    if not users:
        print("  Taşınacak kullanıcı yok.")
        return {}

    with get_cursor() as cur:
        cur.execute("SELECT referral_code FROM users")
        existing_codes = {row["referral_code"] for row in cur.fetchall()}

    migrated: dict[str, str] = {}
    # Stable order (by created_at) so that if member_number must be
    # backfilled, earlier accounts legitimately get earlier numbers.
    ordered_users = sorted(users.values(), key=lambda u: u.get("created_at") or "")

    with get_cursor() as cur:
        for user in ordered_users:
            user_id = user["id"]
            cur.execute("SELECT 1 FROM users WHERE id = %s", (user_id,))
            if cur.fetchone() is not None:
                print(f"  {user.get('email')}: zaten taşınmış, atlanıyor.")
                migrated[user_id] = user.get("email", "")
                continue

            referral_code = user.get("referral_code")
            if not referral_code:
                referral_code = _generate_referral_code(
                    user.get("display_name", ""), existing_codes
                )
            existing_codes.add(referral_code)

            member_number = user.get("member_number")
            if member_number is None:
                cur.execute("SELECT nextval('member_number_seq') AS n")
                seq_row = cur.fetchone()
                if seq_row is None:
                    raise RuntimeError("nextval('member_number_seq') satır döndürmedi.")
                member_number = seq_row["n"]

            is_founding_member = user.get("is_founding_member")
            if is_founding_member is None:
                is_founding_member = member_number <= FOUNDING_MEMBER_LIMIT

            cur.execute(
                """
                INSERT INTO users (
                    id, email, password_hash, display_name, created_at,
                    blocked_user_ids, is_moderator, referral_code, referred_by,
                    member_number, is_founding_member
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    user_id,
                    user["email"],
                    user["password_hash"],
                    user["display_name"],
                    _parse_dt(user.get("created_at")),
                    user.get("blocked_user_ids") or [],
                    user.get("email") in _moderator_emails(),
                    referral_code,
                    member_number,
                    is_founding_member,
                ),
            )
            migrated[user_id] = user.get("email", "")
            print(f"  {user['email']}: taşındı (member_number={member_number}).")

    # Second pass: referred_by, only for links where both ends exist.
    with get_cursor() as cur:
        for user in ordered_users:
            referred_by = user.get("referred_by")
            if referred_by and referred_by in migrated:
                cur.execute(
                    "UPDATE users SET referred_by = %s WHERE id = %s",
                    (referred_by, user["id"]),
                )
        # Keep member_number_seq ahead of every migrated/backfilled number,
        # so the next real registration doesn't collide with one of these.
        cur.execute(
            "SELECT setval('member_number_seq', "
            "COALESCE((SELECT MAX(member_number) FROM users), 1))"
        )

    print(f"  Toplam {len(migrated)} kullanıcı işlendi.")
    return migrated


def migrate_sessions() -> None:
    print("\n2. sessions.json -> sessions")
    sessions: dict[str, dict] = _load_json("sessions.json", {})
    if not sessions:
        print("  Taşınacak oturum yok.")
        return
    count = 0
    with get_cursor() as cur:
        for token, session in sessions.items():
            cur.execute(
                """
                INSERT INTO sessions (token, user_id, created_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (token) DO NOTHING
                """,
                (token, session["user_id"], _parse_dt(session.get("created_at"))),
            )
            count += 1
    print(f"  Toplam {count} oturum işlendi.")


def migrate_comments() -> None:
    print("\n3. comments.json -> comments")
    data: dict[str, list[dict]] = _load_json("comments.json", {})
    total = sum(len(v) for v in data.values())
    if not total:
        print("  Taşınacak yorum yok.")
        return
    with get_cursor() as cur:
        for place_id, comments in data.items():
            for c in comments:
                cur.execute(
                    """
                    INSERT INTO comments (
                        id, place_id, author, author_user_id, text, lat, lng, accuracy,
                        created_at, helpful_count, helpful_user_ids,
                        computed_trust_score, flagged_reason, review_status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        c["id"],
                        place_id,
                        c["author"],
                        c.get("author_user_id"),
                        c["text"],
                        c.get("lat"),
                        c.get("lng"),
                        c.get("accuracy"),
                        _parse_dt(c.get("created_at")),
                        c.get("helpful_count", 0),
                        c.get("helpful_user_ids") or [],
                        c.get("computed_trust_score"),
                        c.get("flagged_reason"),
                        c.get("review_status", "visible"),
                    ),
                )
    print(f"  Toplam {total} yorum işlendi.")


def migrate_checkins() -> None:
    print("\n4. checkins.json -> checkins")
    data: dict[str, list[dict]] = _load_json("checkins.json", {})
    total = sum(len(v) for v in data.values())
    if not total:
        print("  Taşınacak check-in yok.")
        return
    with get_cursor() as cur:
        for place_id, checkins in data.items():
            for c in checkins:
                cur.execute(
                    """
                    INSERT INTO checkins (
                        id, place_id, author, author_user_id, lat, lng, accuracy,
                        location_verified, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        c["id"],
                        place_id,
                        c["author"],
                        c.get("author_user_id"),
                        c.get("lat"),
                        c.get("lng"),
                        c.get("accuracy"),
                        c.get("location_verified", False),
                        _parse_dt(c.get("created_at")),
                    ),
                )
    print(f"  Toplam {total} check-in işlendi.")


def migrate_status() -> None:
    print("\n5. status.json -> status_updates")
    data: dict[str, list[dict]] = _load_json("status.json", {})
    total = sum(len(v) for v in data.values())
    if not total:
        print("  Taşınacak durum güncellemesi yok.")
        return
    with get_cursor() as cur:
        for place_id, entries in data.items():
            for e in entries:
                cur.execute(
                    """
                    INSERT INTO status_updates (
                        id, place_id, author, author_user_id, tag, text, created_at,
                        review_status, flagged_reason, helpful_count, helpful_user_ids
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        e["id"],
                        place_id,
                        e["author"],
                        e.get("author_user_id"),
                        e["tag"],
                        e.get("text", ""),
                        _parse_dt(e.get("created_at")),
                        e.get("review_status", "visible"),
                        e.get("flagged_reason"),
                        e.get("helpful_count", 0),
                        e.get("helpful_user_ids") or [],
                    ),
                )
    print(f"  Toplam {total} durum güncellemesi işlendi.")


def migrate_reports() -> None:
    print("\n6. reports.json -> reports")
    reports: list[dict] = _load_json("reports.json", [])
    if not reports:
        print("  Taşınacak şikayet yok.")
        return
    with get_cursor() as cur:
        for r in reports:
            cur.execute(
                """
                INSERT INTO reports (
                    id, reporter_user_id, target_type, target_id, place_id,
                    reason, created_at, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    r["id"],
                    r["reporter_user_id"],
                    r["target_type"],
                    r["target_id"],
                    r["place_id"],
                    r["reason"],
                    _parse_dt(r.get("created_at")),
                    r.get("status", "open"),
                ),
            )
    print(f"  Toplam {len(reports)} şikayet işlendi.")


def migrate_push_subscriptions() -> None:
    print("\n7. push_subscriptions.json -> push_subscriptions")
    data: dict[str, list[dict]] = _load_json("push_subscriptions.json", {})
    total = sum(len(v) for v in data.values())
    if not total:
        print("  Taşınacak push aboneliği yok.")
        return
    with get_cursor() as cur:
        for user_id, subs in data.items():
            for s in subs:
                cur.execute(
                    """
                    INSERT INTO push_subscriptions (user_id, endpoint, p256dh, auth, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, endpoint) DO NOTHING
                    """,
                    (
                        user_id,
                        s["endpoint"],
                        s["keys"]["p256dh"],
                        s["keys"]["auth"],
                        _parse_dt(s.get("created_at")),
                    ),
                )
    print(f"  Toplam {total} push aboneliği işlendi.")


def main() -> int:
    print("=== KesfetPlus JSON -> PostgreSQL tek seferlik veri taşıma ===")
    migrate_users()
    migrate_sessions()
    migrate_comments()
    migrate_checkins()
    migrate_status()
    migrate_reports()
    migrate_push_subscriptions()
    print("\nTaşıma tamamlandı.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
