# Dynamic Retail Pricing Via Multi-Armed Bandits Design

## Purpose

Build a portfolio-quality and research-grounded dynamic retail pricing project. The project will combine a reusable Python Multi-Armed Bandit engine, a real retail data pipeline, reproducible experiments, and a polished React dashboard.

The project will use real data when available and synthetic fallback data when needed. The primary real source is the UCI Online Retail dataset, which contains UK online retail transactions from December 1, 2010 through December 9, 2011, including product, quantity, invoice date, unit price, customer, and country fields. The deployed dashboard will use a small committed sample so the app can run reliably without downloading the full dataset at runtime.

## Goals

- Provide a clear ML/research story around exploration, exploitation, revenue, and regret.
- Demonstrate dynamic pricing with Epsilon-Greedy, UCB1, Sliding-Window UCB, Thompson Sampling, and an oracle baseline.
- Use real retail transactions for data grounding, with transparent simulation assumptions for counterfactual pricing.
- Ship a polished dashboard with an executive Overview tab and an interactive research Lab tab.
- Keep the codebase deployable with Vercel for the frontend and Render for the backend.

## Non-Goals

- Do not build a production retail pricing service.
- Do not integrate with payment, inventory, ERP, or ecommerce systems.
- Do not claim causal proof of counterfactual demand from observational transaction data.
- Do not build auth, admin roles, or multi-tenant account management.
- Do not require full dataset download during deployed app startup.

## Repository Structure

```text
backend/
  app/
    main.py
    routers/
    services/
    schemas/
  mab/
    algorithms/
    environments/
    metrics.py
    simulation.py
  pipelines/
    download_data.py
    clean_data.py
    make_sample.py
  experiments/
    configs/
    run_experiment.py
    results/
  tests/
frontend/
  src/
    api/
    components/
    pages/
    charts/
    state/
  public/
data/
  raw/
  processed/
  samples/
notebooks/
  01_data_exploration.ipynb
  02_bandit_evaluation.ipynb
docs/
  superpowers/specs/
  deployment.md
```

Raw and full processed datasets will be gitignored. Small demo samples and precomputed result files may be committed under `data/samples/` when they are compact enough for normal repository use.

## Architecture

The core ML logic lives in `backend/mab`. API routes and notebooks consume this package rather than duplicating algorithm logic.

FastAPI exposes stable endpoints for dataset metadata, precomputed results, and live simulations. React/Vite renders dashboard views and calls FastAPI through a configurable `VITE_API_BASE_URL`.

The frontend and backend deploy independently:

- Vercel hosts `frontend`.
- Render hosts `backend`.
- Backend CORS allows local frontend dev and the deployed Vercel URL.

This split keeps the research engine testable, the API thin, and the dashboard deployable.

## Data Pipeline

The pipeline will prefer the UCI Online Retail dataset and fall back to synthetic data only when download or local processing is unavailable.

Pipeline stages:

1. Download the UCI dataset through `ucimlrepo` or a direct UCI download path.
2. Load the transaction data into pandas.
3. Clean transactions:
   - remove cancellation invoices and returns
   - require positive `Quantity`
   - require positive `UnitPrice`
   - parse `InvoiceDate`
   - normalize product identifiers and descriptions
   - compute `revenue = Quantity * UnitPrice`
4. Select products or categories with enough historical observations.
5. Save full processed data locally under `data/processed/`.
6. Save a compact deploy-safe sample under `data/samples/`.

The README and dashboard will cite the UCI Online Retail dataset and its license.

## Simulation Environments

Historical retail data does not directly reveal demand at prices the seller did not choose. The project will make that limitation explicit and provide two transparent simulation environments.

### Empirical Arm Environment

Historical unit prices for a selected product or category become arms. Rewards are sampled from observed historical revenue or quantity at each price arm.

This environment is simple and honest because it stays close to observed data. It is not a causal counterfactual model.

### Elasticity Environment

The pipeline fits a simple demand response model from historical price and quantity patterns at product or category level. The simulator then evaluates nearby price arms by sampling demand from the fitted curve with controlled noise, seasonality, or drift.

This environment is more expressive and supports stronger demos, but the UI and docs will label it as simulation based on historical transactions.

## Algorithms

Version 1 includes:

- Epsilon-Greedy
- UCB1
- Sliding-Window UCB
- Thompson Sampling
- Oracle baseline

Each algorithm exposes a common interface:

- initialize with arms and optional random seed
- select an arm
- update with observed reward
- return inspectable state for charts and debugging

The oracle baseline is not a deployable policy. It is only used to compute regret in known simulation environments.

## Metrics

Experiments produce:

- cumulative revenue
- cumulative regret versus oracle
- average reward over time
- arm selection distribution
- final revenue lift versus baseline
- stability across repeated random seeds
- algorithm-specific diagnostics where useful, such as confidence behavior or exploration rate

The experiment runner accepts product/category, environment type, horizon, seeds, algorithm list, and algorithm parameters. It returns trace data for charts and summary rows for tables.

## Backend API

Core endpoints:

- `GET /health`
- `GET /datasets`
- `GET /experiments/precomputed`
- `POST /experiments/run`

`/experiments/run` accepts a compact simulation request and returns chart-ready trace arrays plus summary metrics. Requests should be bounded so live dashboard runs remain fast on Render.

Errors return structured JSON with clear messages for invalid product IDs, missing sample data, unsupported algorithms, and invalid parameters.

## Frontend UX

The dashboard uses two primary tabs.

### Overview

The Overview tab is for recruiters, portfolio viewers, and nontechnical users.

It includes:

- KPI strip for best strategy, revenue lift, regret reduction, explored products, and dataset source
- main revenue/regret comparison chart
- strategy comparison table
- short narrative explaining exploration, exploitation, and why uncertainty-aware methods can outperform naive baselines
- dataset card citing UCI Online Retail and explaining the cleaned sample

### Lab

The Lab tab is for ML reviewers and technical users.

It includes:

- controls for product/category, environment type, horizon, seed, algorithm selection, epsilon, and sliding-window size
- run button that calls FastAPI live simulation
- cumulative regret chart
- cumulative revenue chart
- arm selection share chart
- reward trend chart
- concise winner/caveat summary

The first screen should be the usable dashboard, not a marketing landing page.

## Testing And Verification

Backend verification:

- `pytest` passes.
- algorithm tests use fixed seeds.
- each algorithm chooses only valid arms.
- regret is nonnegative against oracle in fixed environments.
- Sliding-Window UCB forgets observations outside the configured window.
- FastAPI schemas validate request and response shapes.
- `/health`, `/datasets`, `/experiments/precomputed`, and `/experiments/run` work locally.

Frontend verification:

- `npm run build` passes.
- dashboard renders with committed sample data.
- Overview loads precomputed results.
- Lab runs at least one live simulation against local FastAPI.
- browser console has no relevant runtime errors.

End-to-end verification:

- start backend locally
- start frontend locally
- load dashboard
- verify Overview charts and tables
- run one Lab experiment
- document exact commands and results in the final completion note

## Deployment Plan

Deployment target:

- Vercel for `frontend`
- Render for `backend`

Frontend environment:

- `VITE_API_BASE_URL=https://<render-service-url>`

Backend environment:

- allowed CORS origins for local dev and Vercel deployment
- optional data mode flag for committed sample versus full local dataset

Deployment docs will describe:

- local setup
- dataset pipeline commands
- backend deployment on Render
- frontend deployment on Vercel
- environment variables
- health-check verification
- known limitations

## Implementation Order

1. Scaffold monorepo structure.
2. Build Python MAB interfaces, algorithms, metrics, and tests.
3. Build UCI data pipeline and synthetic fallback.
4. Build empirical and elasticity environments.
5. Build experiment runner and precomputed sample outputs.
6. Build FastAPI endpoints and schemas.
7. Build React/Vite dashboard.
8. Add docs, README, and deployment guide.
9. Run backend, frontend, and end-to-end verification.

## Open Decisions Fixed For Version 1

- Build both research engine and interactive web demo.
- Use real UCI data if available, synthetic fallback otherwise.
- Use hybrid empirical and elasticity simulation environments.
- Optimize for portfolio quality and ML/research depth.
- Use FastAPI backend and React/Vite frontend.
- Deploy with Vercel frontend and Render backend.
- Use a monorepo layout.
