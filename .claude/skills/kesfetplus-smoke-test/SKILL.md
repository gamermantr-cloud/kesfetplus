---
name: kesfetplus-smoke-test
description: Runs a real end-to-end HTTP smoke test against the running KesfetPlus backend - checkin, status, and comment/trust-scoring endpoints, including a duplicate-text regression check - and cleans up its own test data afterwards. Use when the user asks to smoke test, sanity check, or verify the backend's checkin/status/trust-scoring endpoints actually work, or after changing checkins_store.py, trust_scoring.py, comments_store.py, or api/main.py.
allowed-tools: PowerShell, Bash
paths:
  - database/checkins_store.py
  - database/trust_scoring.py
  - database/comments_store.py
  - api/main.py
---

## What this does

Hits the real, already-running FastAPI backend with actual HTTP requests
(no mocking, no in-process TestClient) to exercise the parts of the app
that currently have **zero automated test coverage**:

- `POST/GET /places/{id}/checkins`, `/checkin-count`
- `POST/GET /places/{id}/status` (including tag validation)
- `POST /places/{id}/comments` and the trust-scoring pipeline
  (`database/trust_scoring.py`), including a regression check that
  duplicate text is actually detected and scored lower.

All test data is written with a throwaway author prefixed
`SMOKE-TEST-<random>`, and the script deletes exactly those rows from
`database/comments.json`, `database/checkins.json`, and
`database/status.json` when it's done - never touching real user data.

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
   three JSON stores:

   ```
   git status --ignored database/comments.json database/checkins.json database/status.json
   ```

   (These files are gitignored - real user submissions, not source - so
   `git diff` won't show them; the script's own before/after snapshot
   comparison is the real integrity check, printed as part of the summary.)

## Notes

- No new dependency: `requests` is already in `api/requirements.txt` and
  installed in `venv`.
- The script reads the first real `place_id` from
  `database/seed/places.json` - never a made-up id - and imports
  `STATUS_TAGS` from `database/checkins_store.py` and
  `TEXT_SIMILARITY_THRESHOLD` from `database/trust_scoring.py` rather than
  hardcoding them, so it stays correct if those constants change.
- This is a manual/on-demand check (`/kesfetplus-smoke-test`), not wired
  into CI or pre-commit.
