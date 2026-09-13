# KesfetPlus

KesfetPlus is an AI-powered discovery and verification platform. In its
final form it will help people discover places, restaurants, hotels,
activities, events, and nature locations — and it will help verify
business/advertisement information using AI and a trust-scoring system.

## What we are building right now

This repository currently contains only the **foundation**:

- A minimal FastAPI backend with two endpoints (`/` and `/health`).
- A minimal LangGraph "Scout Agent" that proves our AI-orchestration
  setup works (it does not call the internet or any external service
  yet).
- No database connection yet (PostgreSQL will be added later).
- No frontend yet.
- No external/paid APIs connected yet.

## Project structure

```
kesfetplus/
│
├── api/
│   ├── main.py            # FastAPI application
│   └── requirements.txt   # Python packages needed for the backend
│
├── agents/
│   ├── __init__.py
│   └── scout_agent.py     # Minimal LangGraph agent
│
├── database/
│   └── README.md          # Notes on the future PostgreSQL setup
│
├── docs/
│   └── ARCHITECTURE.md    # Architecture explained in simple Turkish
│
├── scripts/
│   └── README.md          # Placeholder for future helper scripts
│
├── .env.example            # Example environment variables (no secrets)
├── .gitignore
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

## What's next

See `docs/ARCHITECTURE.md` for a beginner-friendly (Turkish) explanation
of the architecture and the planned next steps.
