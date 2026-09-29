# Database

There is no PostgreSQL connection yet — but this folder is **not empty
notes anymore**. It holds a real, working file-based data layer plus the
real seed dataset.

## What's actually here today

- **`seed/`** — the real venue dataset: `places.json` (132), `gurme.json`
  (93), `hotels.json` (18), 243 real Istanbul venues total. This is the
  source of truth the frontend reads from (mirrored into
  `frontend/public/data/` — kept in sync by the
  `.claude/skills/kesfetplus-veri-kontrol` check).
- **`comments_store.py`** — a JSON-file-backed store (`comments.json`,
  gitignored — real user data, not committed) for the live comment
  system exposed at `/places/{id}/comments`. Every comment gets a
  trust score (see below) before it's saved.
- **`trust_scoring.py`** — computes a 0-100 trust score per comment from
  location consistency, text-similarity (duplicate/spam detection), and
  submission-velocity signals. Comments scoring below the visibility
  threshold are hidden from the public list; nothing is deleted.
- **`checkins_store.py`** — a JSON-file-backed store (`checkins.json`,
  `status.json`, both gitignored) for the "anlık bilgi akışı" (real-time
  presence) feature: location-optional check-ins and short status
  updates that expire after a few hours.

All three stores follow the same pattern: plain JSON files, a
`threading.Lock` for safe concurrent writes, and no demo/example data
seeded in — they start empty and only ever contain real submissions.

## Why PostgreSQL, and why not yet?

PostgreSQL is still the planned home for this data (places, reviews,
check-ins, trust scores) as the project grows past file-based storage.
It hasn't been added yet because the file-based approach has been
sufficient at the current scale (243 venues, a small number of live
submissions) and migrating early would mean guessing at a schema before
the data model has settled.

## What will happen later

- PostgreSQL (+ PostGIS for geo queries) as a running service, per the
  plan in `docs/research/turkiye-pazar-teknik-mimari.md`.
- The three JSON stores above become real tables; the store modules'
  function signatures are written so the API layer (`api/main.py`)
  shouldn't need to change much when that migration happens.

For anything more current than this file, check `CLAUDE.md` in the repo
root.
