# Database

PostgreSQL-backed now - the ephemeral-disk warning this file used to carry
is resolved. This folder holds the schema, the real seed dataset, and the
store modules the API talks to.

## What's actually here today

- **`schema.sql`** - every `CREATE TABLE`/`CREATE INDEX` statement
  (`venues`, `users`, `sessions`, `comments`, `checkins`, `status_updates`,
  `reports`, `push_subscriptions`). Idempotent (`IF NOT EXISTS` throughout)
  - safe to re-run against a database that already has these tables.
- **`db.py`** - the connection pool every store module uses
  (`get_cursor()`). Reads `DATABASE_URL` from the environment lazily (on
  first real use, not at import time), so the package stays importable
  even before a database is configured; see "Local setup" below for what
  happens if you call a store function without one.
- **`seed/`** - the real venue dataset: `places.json`, `gurme.json`,
  `hotels.json` (485 real Istanbul venues total, as of this migration -
  CLAUDE.md's "243" figure predates several seed-data additions). This
  is still the source of truth the *frontend* reads from directly
  (mirrored into `frontend/public/data/` - kept in sync by the
  `.claude/skills/kesfetplus-veri-kontrol` check); `scripts/seed_venues.py`
  additionally loads it into the `venues` table for backend-side use.
- **`comments_store.py`, `checkins_store.py`, `users_store.py`,
  `reports_store.py`, `push_subscriptions_store.py`** - PostgreSQL-backed
  now (used to be JSON files guarded by a `threading.Lock` - see git
  history for that version). Every public function keeps the exact same
  name/signature/return shape it had as a JSON store, so `api/main.py`
  needed no changes at all. Each module's docstring explains its own
  tables.
- **`trust_scoring.py`** - unchanged logic (still computes a 0-100 trust
  score per comment from location consistency, text-similarity, and
  submission-velocity signals); `comments_store.add_comment` now feeds it
  rows queried from the `comments` table instead of a loaded JSON file.
- **`push_notify.py`, `content_filter.py`, `photo_compare.py`,
  `places_photo_proxy.py`, `weather_cache.py`** - not stores (no
  persistent per-user data of their own), untouched by this migration.

## Local setup

1. Get a PostgreSQL server running somewhere you can reach - any of these
   work the same way, since the app only ever talks to `DATABASE_URL`:
   - Docker (simplest for local dev):
     `docker run --name kesfetplus-pg -e POSTGRES_PASSWORD=devpassword -p 5432:5432 -d postgres:16`
   - A native local install.
   - A hosted dev/free tier (Neon, Render, etc. - see
     docs/research/turkiye-pazar-teknik-mimari.md for the planned
     production stack; opening a real hosting account is a deliberately
     separate step from this migration).
2. Set `DATABASE_URL` in `.env` (see `.env.example`), e.g. for the Docker
   command above: `postgresql://postgres:devpassword@localhost:5432/postgres`.
3. Apply the schema once:
   `venv\Scripts\python.exe -c "import os,psycopg,dotenv;dotenv.load_dotenv();psycopg.connect(os.environ['DATABASE_URL']).execute(open('database/schema.sql',encoding='utf-8').read())"`
   (or `psql "$DATABASE_URL" -f database/schema.sql` if you have the
   `psql` client).
4. Load the venue catalog: `venv\Scripts\python.exe scripts\seed_venues.py`.
5. If you have real data in the old JSON files from before this migration
   (gitignored - `database/{comments,checkins,status,users,sessions,
   reports,push_subscriptions}.json`), run the one-time migration:
   `venv\Scripts\python.exe scripts\migrate_json_to_postgres.py`. Idempotent
   - safe to re-run.
6. Start the backend as usual (`venv\Scripts\uvicorn.exe api.main:app --reload`).

Without `DATABASE_URL` set, the package still imports fine (so e.g. `ruff`/
`mypy` work with no database running), but any store function that
actually needs the database raises `database.db.DatabaseNotConfiguredError`
with the steps above in its message - never a fabricated "success".

## Why PostgreSQL, and why not PostGIS yet

PostgreSQL replaces file-based storage per the plan in
`docs/research/turkiye-pazar-teknik-mimari.md`. **PostGIS is deliberately
not included yet**: seed venues only carry an approximate district-center
coordinate (see `frontend/src/lib/districts.js`), not a real per-venue GPS
address, so adding spatial indexes now would mean fabricating
precise-looking coordinates that don't exist - forbidden by this project's
"sahte veri yasak" rule (see CLAUDE.md). PostGIS is a later phase, once
real per-venue coordinates exist.

`venues` uses a hybrid schema per the same research doc's recommendation:
fixed columns for what's actually filtered on (`id`, `category`, `name`,
`district`), a `JSONB raw_data` column for everything else - places/gurme/
hotels each carry a different and still-evolving set of fields, so forcing
them into one wide fixed-column table would mean a lot of always-NULL
columns per category.

For anything more current than this file, check `CLAUDE.md` in the repo
root.
