---
name: kesfetplus-smoke-test
description: Runs a real end-to-end HTTP smoke test against the running KesfetPlus backend - auth (register/login/token), checkin/status/comment/trust-scoring, content filtering, reporting/blocking, and photo comparison - and cleans up its own test data afterwards. Use when the user asks to smoke test, sanity check, or verify the backend actually works, or after changing checkins_store.py, comments_store.py, trust_scoring.py, users_store.py, reports_store.py, content_filter.py, photo_compare.py, or api/main.py.
allowed-tools: PowerShell, Bash
paths:
  - database/checkins_store.py
  - database/comments_store.py
  - database/trust_scoring.py
  - database/users_store.py
  - database/reports_store.py
  - database/content_filter.py
  - database/photo_compare.py
  - api/main.py
---

## What this does

Hits the real, already-running FastAPI backend with actual HTTP requests
(no mocking, no in-process TestClient) to exercise the parts of the app
that have little/no other automated test coverage:

- **Auth**: `POST /auth/register` (201), `POST /auth/login` with a wrong
  password (401) and with the correct one (token returned), and a
  token-less content `POST` (401) - posting content now requires a real
  account (App Store Guideline 1.2).
- **Check-in / status / comment / trust-scoring**, now posted as an
  authenticated user (Bearer token) instead of a free-text `author` field:
  `POST/GET /places/{id}/checkins`, `/checkin-count`, `POST/GET
  /places/{id}/status` (incl. tag validation), `POST /places/{id}/comments`
  and the trust-scoring pipeline (`database/trust_scoring.py`), including a
  regression check that duplicate text is detected and scored lower.
- **Content filtering** (`database/content_filter.py`): a comment
  containing one known objectionable term is forced to
  `review_status="hidden"` / `flagged_reason="objectionable_content"`.
  Only ever uses a single term from that module's own list to exercise the
  *behavior* - never reproduces the list itself here.
- **Reporting / blocking** (`database/reports_store.py`,
  `database/users_store.py`): a second test user (B) posts a comment, the
  first (A) reports it (`POST /reports` -> 201, shows up in `GET
  /reports`), then blocks B (`POST /users/{id}/block`) and the test
  verifies B's comment is actually excluded from A's `GET
  /places/{id}/comments` server-side - then re-appears after `POST
  /users/{id}/unblock`.
- **Photo comparison** (`database/photo_compare.py`): finds a real venue
  with a reference photo in the seed data, re-uploads that same photo to
  `POST /places/{id}/compare-photo` and checks for a high/"muhtemelen_ayni_yer"
  similarity, then uploads an unrelated synthetic image and checks the
  verdict is *not* "muhtemelen_ayni_yer".

Deliberately **out of scope**: any moderator/admin panel endpoints (e.g.
anything gated by a `MODERATOR_EMAILS`-style mechanism). That is a
separate, independently-evolving feature area - this script must not
depend on it or assume it's stable.

All test data (two accounts, their sessions, comments, a checkin, a status
update, a report) is tagged with a throwaway `SMOKE-TEST-<run id>` marker
(account display names, and therefore the `author` field written into
comments/checkins/status), and the script deletes exactly those rows from
`database/comments.json`, `database/checkins.json`, `database/status.json`,
`database/users.json`, `database/sessions.json`, and `database/reports.json`
when it's done - never touching real user data.

## Prerequisite

The backend must already be running on `http://127.0.0.1:8000`. This
skill does **not** start it - use the `kesfetplus-dev` skill first if it's
not up. The script itself refuses to report false "tests passed" if
`/health` doesn't respond; it fails loudly instead.

## Instructions

1. Confirm the backend is up (or start it via `kesfetplus-dev` first):

   ```
   powershell -NoProfile -ExecutionPolicy Bypass -Command "try { (Invoke-WebRequest -Uri http://127.0.0.1:8000/health -UseBasicParsing -TimeoutSec 5).StatusCode } catch { 'DOWN' }"
   ```

2. Run the smoke test with the project's venv Python (needs `database.*`
   importable, which the script handles by adding the repo root to
   `sys.path`; no need to `cd` first):

   ```
   C:\AI-SYSTEM\kesfetplus\venv\Scripts\python.exe C:\AI-SYSTEM\kesfetplus\.claude\skills\kesfetplus-smoke-test\scripts\smoke_test.py
   ```

3. Read the printed summary (`X gecti, Y basarisiz`) and exit code
   (0 = all passed, 1 = at least one failed or the backend was down).
   On failure, the script lists which specific checks failed and why -
   read those instead of re-running blind.

4. The script always attempts cleanup (`finally` block) even if a test
   assertion fails midway, and prints per-file "restored to pre-test
   state" checks. If you want to double-check nothing leaked, diff the
   six JSON stores:

   ```
   git status --ignored database/comments.json database/checkins.json database/status.json database/users.json database/sessions.json database/reports.json
   ```

   (These files are gitignored - real user submissions, not source - so
   `git diff` won't show them; the script's own before/after snapshot
   comparison is the real integrity check, printed as part of the summary.)

## Notes

- No new dependency: `requests` and `Pillow` are already in
  `api/requirements.txt` and installed in `venv`.
- The script reads the first real `place_id` from
  `database/seed/places.json`, and separately finds a real place with a
  reference photo by scanning `places.json`/`gurme.json`/`hotels.json` and
  asking `database/photo_compare.get_reference_photo_url` for its URL -
  never a made-up id or URL. It imports `STATUS_TAGS` from
  `checkins_store.py` and `TEXT_SIMILARITY_THRESHOLD` from
  `trust_scoring.py` rather than hardcoding them, so it stays correct if
  those constants change.
- **The photo-compare test makes real network calls to Wikimedia Commons**
  (once from the script itself, once more from the backend on every
  `compare-photo` call - so 3 requests to the same URL per run). Wikimedia
  rate-limits aggressive/back-to-back callers (observed: a 429 -> the
  backend correctly surfaces this as a 502 `ReferenceDownloadError`, not a
  fabricated score). If you run this skill twice in quick succession and
  only the photo-compare checks fail with a 502/429, that's expected
  external flakiness, not a regression - wait a bit and re-run just that
  section, or re-run the whole script after a short pause.
- Account emails/passwords used here are synthetic, single-run throwaway
  values (`smoke-test-<run id>-{a,b}@example.test`) - not real credentials
  and not reused across runs.
- This is a manual/on-demand check (`/kesfetplus-smoke-test`), not wired
  into CI or pre-commit.
