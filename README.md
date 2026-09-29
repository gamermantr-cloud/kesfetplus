# KesfetPlus

KesfetPlus is an AI-powered discovery and verification platform. In its
final form it will help people discover places, restaurants, hotels,
activities, events, and nature locations — and it will help verify
business/advertisement information using AI and a trust-scoring system.

## Current status (updated 2026-09-29)

- **Frontend is live**: `frontend/` is a React 19 + Vite + Tailwind v4
  mobile-first app with 9 screens (Splash, Home, PlaceDetail, AIAssistant,
  ExploreAll, MapView, Messages, Notifications, Profile).
- **Real data**: `database/seed/` holds 243 real Istanbul venues
  (`places.json` 132, `gurme.json` 93, `hotels.json` 18) — no
  placeholder/fake data.
- **Backend has more than a skeleton**: `api/main.py` serves comments
  (`/places/{id}/comments`), check-ins (`/places/{id}/checkins`), and
  status updates (`/places/{id}/status`), backed by file-based JSON
  stores (see `database/README.md`).
- **No PostgreSQL yet** — still planned, see `database/README.md`.
- **Scout Agent** (`agents/scout_agent.py`) calls the real Google Places
  API when `GOOGLE_PLACES_API_KEY` is set; it's a standalone CLI script,
  not wired into any API endpoint yet.
- No other external/paid APIs connected yet.

For the authoritative, actively-maintained project context (architecture,
team, known issues), see **`CLAUDE.md`** — it's kept current on every
change; this README and `docs/ARCHITECTURE.md` are the beginner-friendly
walkthroughs.

## Project structure

```
kesfetplus/
│
├── api/
│   ├── main.py             # FastAPI app: comments, check-ins, status endpoints
│   └── requirements.txt    # Python packages needed for the backend
│
├── agents/
│   ├── __init__.py
│   └── scout_agent.py      # LangGraph agent, calls Google Places API if key is set
│
├── database/
│   ├── README.md           # File-based data layer + future PostgreSQL plan
│   ├── seed/                # Real seed data (places/gurme/hotels, 243 venues)
│   ├── comments_store.py    # Comments + trust-scoring
│   ├── checkins_store.py    # "Anlık bilgi akışı" check-ins/status
│   └── trust_scoring.py     # Comment trust-score signals
│
├── frontend/                # React 19 + Vite + Tailwind, 9 screens
│
├── docs/
│   ├── ARCHITECTURE.md      # Architecture explained in simple Turkish
│   └── research/            # Strategy/technical research reports
│
├── scripts/
│   └── README.md            # Placeholder for future helper scripts
│
├── .claude/                 # Team agents, skills, hooks (see CLAUDE.md)
├── .env.example              # Example environment variables (no secrets)
├── .gitignore
├── CLAUDE.md                 # Authoritative, up-to-date project context
└── README.md
```

## Prerequisites

You need Python 3.10+ installed and available on your system. You can
check this by running `python --version` in PowerShell. If that command
does not work, install Python from https://www.python.org/downloads/
first (make sure to check "Add Python to PATH" during installation).

## 1. Create a virtual environment

A virtual environment keeps this project's Python packages separate
from everything else on your computer. From the `kesfetplus` folder,
run:

```powershell
python -m venv venv
```

## 2. Activate it on Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks this with a permissions error, you may need to run
this once (in an admin PowerShell) to allow local scripts:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

You'll know it worked when you see `(venv)` at the start of your
PowerShell prompt.

## 3. Install dependencies

```powershell
pip install -r api\requirements.txt
```

## 4. Start the FastAPI server

```powershell
uvicorn api.main:app --reload
```

By default this starts the server at `http://127.0.0.1:8000`.

## 5. Test the API

With the server running, open a new browser tab (or use another
terminal) and visit:

- http://127.0.0.1:8000/ — should return `{"name": "KesfetPlus", "status": "running"}`
- http://127.0.0.1:8000/health — should return `{"status": "healthy"}`
- http://127.0.0.1:8000/docs — FastAPI's automatic interactive API docs

## 6. Run the Scout Agent

With the virtual environment activated, run:

```powershell
python agents\scout_agent.py
```

This should print something like:

```
{'city': 'Istanbul', 'status': 'ready', 'message': 'Scout agent is ready to search for discovery candidates.'}
```

## 7. Run the frontend

In a separate terminal, from the `frontend` folder:

```powershell
npm install
npm run dev
```

This starts Vite at `http://localhost:5173`, which proxies `/api`
requests to the backend at `http://127.0.0.1:8000` (see
`frontend/vite.config.js`) — so run the backend first.

## What's next

`CLAUDE.md` (repo root) is the up-to-date source of truth for project
state, architecture, and the team's known issues/backlog. `docs/ARCHITECTURE.md`
has a beginner-friendly (Turkish) explanation of the original foundation
and planned next steps (note: it now carries a note pointing back to
`CLAUDE.md` for anything that's changed since).
