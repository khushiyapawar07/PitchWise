# PitchWise — Phase 6 deployment (Vercel + Render)

Deploy **frontend** on Vercel and **backend** on Render. End users never configure API keys; you set secrets in Render only.

## Prerequisites

- GitHub (or GitLab) repo with this project pushed
- [Render](https://render.com) account
- [Vercel](https://vercel.com) account
- `data/processed/` committed (~9 MB) — required on Render (raw JSON optional)
- `data/metadata/` committed

Local check before deploy:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

---

## 1. Deploy backend (Render)

1. **New → Web Service** → connect your repository.
2. **Root directory:** `backend`
3. **Runtime:** Python 3.12
4. **Build command:** `pip install -r requirements.txt`
5. **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Health check path:** `/health`

### Environment variables (Render dashboard)

| Variable | Value |
|----------|--------|
| `GEMINI_API_KEY` | Your Google AI Studio key (Secret) |
| `GEMINI_MODEL` | `gemini-3.8-flash` |
| `GEMINI_TIMEOUT_MS` | `120000` |
| `CORS_ORIGINS` | Your Vercel URL, e.g. `https://pitchwise.vercel.app` (add preview URL too if needed) |
| `DATA_PROCESSED_DIR` | `../data/processed` |
| `DATA_METADATA_DIR` | `../data/metadata` |
| `DATA_RAW_DIR` | `../data/raw` (optional if processed data present) |

7. Deploy and copy the public URL, e.g. `https://pitchwise-api.onrender.com`
8. Verify: `https://YOUR-API.onrender.com/health` → `{"status":"ok","ai_configured":true}`

**Note:** Free Render services spin down when idle; first request may take ~30–60s.

Alternative: use repo-root `render.yaml` Blueprint if your Render account supports it.

---

## 2. Deploy frontend (Vercel)

1. **Add New Project** → import the same repository.
2. **Root Directory:** `frontend`
3. **Framework preset:** Vite
4. **Build command:** `npm run build`
5. **Output directory:** `dist`

### Environment variables (Vercel)

| Variable | Value |
|----------|--------|
| `VITE_API_BASE_URL` | `https://YOUR-API.onrender.com` (no trailing slash) |

6. Deploy and open the Vercel URL.

7. **Update Render `CORS_ORIGINS`** to include the exact Vercel production URL, then redeploy the API if the browser blocks requests.

`frontend/vercel.json` enables React Router (SPA fallback to `index.html`).

---

## 3. Post-deploy smoke test

1. Open Vercel URL → select demo match
2. Venue stats load (114 Wankhede matches)
3. Players → Compare two players
4. AI → Ask (needs quota on Gemini free tier)

---

## 4. What not to deploy

- `backend/.env` — never commit; use Render env vars only
- `backend/.venv/`, `node_modules/`
- `data/raw/` — optional on Render if `data/processed/` is present (smaller/faster deploy)

---

## 5. Troubleshooting

| Issue | Fix |
|-------|-----|
| CORS error in browser | Set `CORS_ORIGINS` on Render to your Vercel origin |
| 404 on refresh / deep links | Ensure `frontend/vercel.json` rewrites are deployed |
| API 502 on first hit | Render cold start; retry |
| AI unavailable | `GEMINI_API_KEY` on Render; check quota (429) |
| Empty stats | Ensure `data/processed` exists in repo at deploy time |
