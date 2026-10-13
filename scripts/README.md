# Scripts

Helper scripts for this project.

## `seed_venues.py` — load the venue catalog into PostgreSQL

Upserts `database/seed/{places,gurme,hotels}.json` (the real Istanbul venue
dataset) into the `venues` table (`database/schema.sql`). Idempotent - safe
to re-run after the seed files change. Requires `DATABASE_URL` set (see
`database/README.md`):

```powershell
venv\Scripts\python.exe scripts\seed_venues.py
```

This does not replace the seed JSON files or the frontend's direct read of
them (`frontend/src/lib/data.js`) - it only makes the same data available
to the backend.

## `migrate_json_to_postgres.py` — one-time JSON → PostgreSQL data migration

Copies real data that may already exist in the old JSON stores
(`database/{comments,checkins,status,users,sessions,reports,
push_subscriptions}.json` - gitignored, see `.gitignore`) into the new
PostgreSQL tables. Idempotent (`ON CONFLICT ... DO NOTHING`, keyed on each
row's original id) - safe to re-run. Requires `DATABASE_URL` set and
`database/schema.sql` already applied:

```powershell
venv\Scripts\python.exe scripts\migrate_json_to_postgres.py
```

Only needed once per machine that was running the old file-based backend
with real data on it - a brand-new setup with empty JSON stores has
nothing to migrate.

## `generate_vapid_keys.py` — Web Push (VAPID) key generation

Generates a real VAPID (RFC 8292) key pair for the Web Push notification
feature (see `database/push_notify.py`, `database/push_subscriptions_store.py`,
`api/main.py` `/push/*` endpoints). VAPID is a **self-generated** key pair -
no third-party account, signup, or API key is needed (unlike the older
FCM/APNs-only approach).

Run once per environment (dev and prod should each have their own pair),
from the project root with the virtual environment set up:

```powershell
venv\Scripts\python.exe scripts\generate_vapid_keys.py
```

This prints three lines - copy them into your local `.env` (never commit
`.env`, see `.gitignore`):

```
VAPID_PUBLIC_KEY=...
VAPID_PRIVATE_KEY=...
VAPID_CLAIMS_EMAIL=mailto:you@example.com
```

Replace `VAPID_CLAIMS_EMAIL` with a real contact address you control - RFC
8292 requires it (push services may use it to reach you about abuse).

Without these three variables set, `GET /push/vapid-public-key` honestly
returns 503 ("VAPID anahtarları henüz üretilmedi") instead of a fake key,
and `database/push_notify.py` logs that it's skipping the send rather than
pretending to have sent a notification - see that module's docstring.
