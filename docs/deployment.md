# Deployment Guide

This project is deployed as two services:

- Frontend: Vercel, rooted at `frontend/`
- Backend: Render, rooted at `backend/`

## Render Backend Service

Use a Python web service on Render with `backend/` as the root directory.

Build command:

```powershell
python -m pip install -e .[dev]
```

Start command:

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Required backend env var:

- `FRONTEND_ORIGINS`: comma-separated list of allowed browser origins, such as your Vercel URL and any local dev origins.

Notes:

- The backend CORS allowlist defaults to `http://localhost:5173` and `http://127.0.0.1:5173` when `FRONTEND_ORIGINS` is not set.
- The API exposes `/health`, `/datasets`, `/experiments/precomputed`, and `/experiments/run`.

## Vercel Frontend Service

Use `frontend/` as the project root in Vercel.

Required frontend env var:

- `VITE_API_BASE_URL`: the public Render backend URL, for example `https://<your-render-service>.onrender.com`

Important:

- `VITE_API_BASE_URL` is a Vite build-time variable. Set it before the production build so the bundled frontend points at the correct backend.
- The frontend falls back to `http://127.0.0.1:8000` only during local development when the variable is unset.

## Post-Deploy Checks

1. Open `https://<render-service>/health` and confirm `{"status":"ok"}`.
2. Open `https://<render-service>/datasets` and confirm the catalog loads.
3. Open the Vercel frontend and confirm the Overview tab renders.
4. Run a Lab experiment from the frontend and confirm the backend returns a summary and trace set.
