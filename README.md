# Dynamic Retail Pricing Dashboard

Dynamic Retail Pricing Dashboard is a FastAPI + React lab for comparing multi-armed bandit pricing policies on retail transaction data. It pairs a real dataset pipeline with a hybrid simulator, then surfaces the results in a clean Overview tab and an interactive Lab tab so you can inspect revenue, regret, and arm-selection behavior without wading through notebook output.

## Screenshots

Screenshots will be added after local browser verification.

## What Makes It Different

- Real retail data pipeline built around the UCI Online Retail dataset, with a committed sample so the demo works without a runtime download.
- Hybrid simulation layer that supports both empirical replay and an elasticity-based environment.
- Algorithm comparison across epsilon-greedy, UCB1, sliding-window UCB, and Thompson sampling, with an oracle upper bound shown in the precomputed overview.
- Polished lab UI with KPI cards, charts, strategy tables, and direct controls for running experiments.

## Architecture

```text
UCI Online Retail data
        |
        v
backend/pipelines -> data/samples/catalog.json + precomputed_results.json
        |
        v
FastAPI backend (backend/app/main.py)
  |        |         |
  |        |         +--> /experiments/run
  |        +--------------> /datasets
  +-----------------------> /health
        |
        v
React + Vite frontend (frontend/src/App.tsx)
  |                         |
  |                         +--> Overview tab (precomputed comparison)
  +----------------------------> Lab tab (live experiment runner)
```

## Algorithms

- Epsilon-greedy: explores with a fixed epsilon, then exploits the best observed arm.
- UCB1: uses optimism under uncertainty to balance exploration and exploitation.
- Sliding-window UCB: focuses on recent reward history so the policy can adapt to non-stationary behavior.
- Thompson sampling: samples from posterior beliefs to choose the next arm probabilistically.
- Oracle: included in the precomputed overview as an upper bound for comparison, not as a normal Lab choice.

## Data And Limitations

- Primary source: UCI Machine Learning Repository, Online Retail dataset. The code downloads the workbook from `https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx`.
- The deployed demo uses committed sample data in `data/samples/` so it can start reliably without downloading the full dataset at runtime.
- Counterfactual demand is simulated from historical transactions, not causal proof. The dashboard demonstrates policy behavior, not a causal claim that a price change will produce the same lift in production.

## Local Setup

Backend:

```powershell
cd backend
python -m pip install -e .[dev]
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Experiment Commands

Regenerate the committed precomputed payload:

```powershell
cd backend
python -m experiments.run_experiment --output ..\data\samples\precomputed_results.json
```

Run a live experiment through the API:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/experiments/run -ContentType 'application/json' -Body (@{
  environment = 'elasticity'
  horizon = 200
  seed = 42
  algorithms = @('epsilon_greedy', 'ucb1', 'sliding_window_ucb', 'thompson_sampling')
  parameters = @{
    epsilon_greedy = @{ epsilon = 0.1 }
    sliding_window_ucb = @{ window_size = 50 }
    ucb1 = @{}
    thompson_sampling = @{}
  }
} | ConvertTo-Json -Depth 5)
```

## Test Commands

Backend tests:

```powershell
cd backend
python -m pytest
```

Frontend verification:

```powershell
cd frontend
npm run build
```

## Deployment Overview

- Frontend: deploy `frontend/` to Vercel.
- Backend: deploy `backend/` to Render as a Python web service.
- Set `VITE_API_BASE_URL` in Vercel before the frontend build. Vite inlines that value at build time.
- Set `FRONTEND_ORIGINS` in Render to the deployed Vercel origin plus any local origins you want to allow during testing.
- After deploy, verify `/health`, `/datasets`, the Overview tab, and a Lab run against the live backend.
