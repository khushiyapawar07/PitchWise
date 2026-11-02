# PitchWise

AI-powered cricket decision intelligence for fantasy players (MVP prototype).

**Source of truth:** [PRD.md](./PRD.md), [SRS.md](./SRS.md).

## Demo scenario

- **Match:** Mumbai Indians vs Chennai Super Kings, 14 April 2024, Wankhede Stadium  
- **Cricsheet file:** `data/raw/1426267.json`  
- **Pre-match cutoff:** 13 April 2024 (match `1426267` excluded from historical stats)

## Repository layout

| Path | Purpose |
|------|---------|
| `data/raw/` | Cricsheet IPL JSON (read-only, do not modify) |
| `data/processed/` | Generated index (ETL output) |
| `data/metadata/` | Curated venues, demo match, player roles/styles |
| `backend/` | FastAPI + stats + Gemini (later phases) |
| `frontend/` | React + Tailwind UI |

## Backend (local)

On Windows, `pip` is often not on PATH. Use **`py -3 -m pip`** or the venv’s Python (below).

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

If you prefer activation: `.\.venv\Scripts\Activate.ps1`, then `python -m pip install -r requirements.txt` (use `python -m pip`, not bare `pip`, if `pip` is not on PATH).

Health check: `GET http://127.0.0.1:8000/health`

**Phase 2 API (after processed data is built):**

- `GET /api/matches`
- `GET /api/matches/1426267`
- `GET /api/venues/wankhede_mumbai/stats?match_id=1426267`
- `GET /api/players?match_id=1426267`
- `GET /api/players/{player_id}/stats?match_id=1426267`
- `POST /api/compare` — body: `{ "player_a_id", "player_b_id", "match_id" }`
- `POST /api/ai/insights` — body: `{ "question", "match_id", "player_a_id?", "player_b_id?" }`

**Enable AI:** create `backend/.env` from `.env.example` and set `GEMINI_API_KEY=your_key`, then restart uvicorn.

Interactive docs: `http://127.0.0.1:8000/docs`

## Frontend (local)

Optional until API screens are wired (Phase 6+):

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Opens the PitchWise UI at `http://localhost:5173` (requires backend on port 8000).

**Workflow:** Home → match overview → players → compare → AI insights.

## Build processed data (ETL)

Does **not** modify `data/raw/`.

```powershell
cd backend
.\.venv\Scripts\python.exe scripts\build_processed_data.py
```

Outputs: `data/processed/manifest.json`, `matches.json`, `performances_by_match.json`.

## Tests

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

## Data policy

- All statistics are computed in Python from Cricsheet JSON and processed artifacts.
- Gemini only explains backend-supplied numbers.
- Player metadata in `data/metadata/players_ipl.json` is curated; use `"unknown"` when unavailable.

## Deployment (Vercel + Render)

Step-by-step guide: **[deploy/DEPLOY.md](./deploy/DEPLOY.md)**

**Summary**

1. **Render** — root `backend`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, set `GEMINI_API_KEY` and `CORS_ORIGINS` (your Vercel URL).
2. **Vercel** — root `frontend`, set `VITE_API_BASE_URL` to your Render API URL.
3. Commit `data/processed/` and `data/metadata/` so production has stats without raw JSON.

Repo includes `render.yaml` (Blueprint) and `frontend/vercel.json` (SPA routing).
