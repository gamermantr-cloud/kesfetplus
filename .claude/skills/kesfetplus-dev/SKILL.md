---
name: kesfetplus-dev
description: Starts both KesfetPlus dev servers (FastAPI backend via uvicorn on :8000, React/Vite frontend on :5173) in the background and verifies both are actually up. Use when the user asks to start/run/launch the app, start the dev servers, or boot up backend and frontend for local development.
allowed-tools: PowerShell
---

## What this does

Launches both KesfetPlus dev servers as detached background processes and
health-checks them, instead of starting each one by hand in a separate
PowerShell window:

- Backend: `venv\Scripts\uvicorn.exe api.main:app --reload --port 8000`
- Frontend: `npm run dev` (Vite, default port 5173)

## Instructions

1. Run the start script with the PowerShell tool:

   ```
   powershell -NoProfile -ExecutionPolicy Bypass -File "C:\AI-SYSTEM\kesfetplus\.claude\skills\kesfetplus-dev\scripts\start-dev.ps1"
   ```

2. The script itself waits ~4 seconds and health-checks both servers
   (`GET http://127.0.0.1:8000/health` for the backend, a TCP check on
   port 5173 for the frontend), printing a clear summary. Read that
   summary — do not assume success just because the script exited.

3. If a server is already listening on its port, the script skips
   starting a new one (so re-invoking this skill is safe / idempotent).

4. If either server did NOT come up:
   - Read the matching log file under `C:\AI-SYSTEM\kesfetplus\dev-logs\`
     (`backend.err.log` / `frontend.err.log`) to diagnose why.
   - Common causes: venv not created yet (`python -m venv venv` +
     `pip install -r api\requirements.txt`, see README.md), or
     `node_modules` missing (`npm install` in `frontend\`).

5. Report to the user: which servers are up, their URLs
   (`http://127.0.0.1:8000` and `http://127.0.0.1:5173`), and the
   `/docs` link for the FastAPI Swagger UI (`http://127.0.0.1:8000/docs`).

6. To stop both servers later, run:

   ```
   powershell -NoProfile -ExecutionPolicy Bypass -File "C:\AI-SYSTEM\kesfetplus\.claude\skills\kesfetplus-dev\scripts\stop-dev.ps1"
   ```

## Notes

- Logs are written to `C:\AI-SYSTEM\kesfetplus\dev-logs\` (`backend.out.log`,
  `backend.err.log`, `frontend.out.log`, `frontend.err.log`) — tail these
  instead of re-running the servers in the foreground when debugging.
- Process IDs are recorded in `dev-logs\dev-pids.json` so `stop-dev.ps1`
  can find and stop exactly the processes this skill started.
- Both servers run detached (`Start-Process -WindowStyle Hidden`), so they
  keep running after this PowerShell command returns — no need for
  `run_in_background`.
