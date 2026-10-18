"""Loads the real venue dataset (database/seed/{places,gurme,hotels}.json -
243 real Istanbul places/restaurants/hotels, see CLAUDE.md) into the
`venues` table (database/schema.sql).

This does NOT replace database/seed/*.json or frontend/public/data/*.json -
the frontend still reads those directly (see frontend/src/lib/data.js and
CLAUDE.md's "Mevcut durum"), and that isn't part of this migration. This
script exists so the *backend* also has the real venue data available in
PostgreSQL for future backend-side features (e.g. a venues API, joins
against comments/checkins) without re-reading JSON files - see
docs/research/turkiye-pazar-teknik-mimari.md Bölüm 2A's hybrid-schema
recommendation (fixed columns + a JSONB `raw_data` column) that
database/schema.sql's `venues` table implements.

Idempotent / safe to re-run: every row is upserted by id
(`ON CONFLICT (id) DO UPDATE`), so running this again after the seed JSON
files change (e.g. scripts/fetch_google_places_photos.py added a
photo_name) just refreshes the existing rows - it never duplicates or
fabricates a venue that isn't in the seed files.

Usage (from the project root, with DATABASE_URL set in .env or the shell):
    venv\\Scripts\\python.exe scripts\\seed_venues.py
"""

from __future__ import annotations

import json
import os
import sys

from dotenv import load_dotenv
from psycopg.types.json import Jsonb

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

load_dotenv()

from database.db import get_cursor  # noqa: E402

_SEED_DIR = os.path.join(_REPO_ROOT, "database", "seed")

# filename -> category (must match the venues.category CHECK constraint in
# database/schema.sql).
_SEED_FILES = {
    "places.json": "places",
    "gurme.json": "gurme",
    "hotels.json": "hotels",
    "sahne.json": "sahne",
}


def _load_seed_file(filename: str) -> list[dict]:
    path = os.path.join(_SEED_DIR, filename)
    if not os.path.exists(path):
        print(f"  UYARI: {path} bulunamadı, atlanıyor.")
        return []
    with open(path, encoding="utf-8") as f:
        venues: list[dict] = json.load(f)
    return venues


def seed_venues() -> int:
    """Upserts every venue from every seed file into the `venues` table.
    Returns the total number of rows written."""
    total = 0
    for filename, category in _SEED_FILES.items():
        venues = _load_seed_file(filename)
        print(f"{filename}: {len(venues)} mekan ({category})")
        with get_cursor() as cur:
            for venue in venues:
                venue_id = venue.get("id")
                name = venue.get("name")
                if not venue_id or not name:
                    print(f"  UYARI: id veya name eksik, atlanıyor: {venue!r}")
                    continue
                cur.execute(
                    """
                    INSERT INTO venues (id, category, name, district, raw_data, updated_at)
                    VALUES (%s, %s, %s, %s, %s, now())
                    ON CONFLICT (id) DO UPDATE SET
                        category = EXCLUDED.category,
                        name = EXCLUDED.name,
                        district = EXCLUDED.district,
                        raw_data = EXCLUDED.raw_data,
                        updated_at = now()
                    """,
                    (venue_id, category, name, venue.get("area"), Jsonb(venue)),
                )
                total += 1
    return total


def main() -> int:
    print("=== KesfetPlus venue seed (database/seed/*.json -> venues tablosu) ===\n")
    total = seed_venues()
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM venues")
        row = cur.fetchone()
    current_total = row["n"] if row else 0
    print(f"\nToplam {total} satır işlendi. venues tablosunda şu an {current_total} satır var.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
