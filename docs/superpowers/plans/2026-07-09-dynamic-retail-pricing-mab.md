# Dynamic Retail Pricing MAB Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a research-grounded dynamic retail pricing project with a Python Multi-Armed Bandit engine, real/synthetic retail data pipeline, FastAPI backend, React/Vite dashboard, tests, and deployment docs.

**Architecture:** Keep all ML policy, environment, and metric logic in `backend/mab`; FastAPI routes call services only. React/Vite consumes typed API responses and renders Overview and Lab tabs. Full UCI data stays local/gitignored; committed sample data powers deployed demos.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic, pandas, numpy, pytest, httpx, uvicorn; React 18+, TypeScript, Vite, Recharts, lucide-react; Vercel frontend and Render backend.

## Global Constraints

- Build both research engine and interactive web demo.
- Use real UCI Online Retail data if available, synthetic fallback otherwise.
- Use hybrid empirical and elasticity simulation environments.
- Optimize for portfolio quality and ML/research depth.
- Use FastAPI backend and React/Vite frontend.
- Deploy with Vercel frontend and Render backend.
- Use a monorepo layout.
- Do not claim causal proof of counterfactual demand from observational transaction data.
- Do not require full dataset download during deployed app startup.
- Raw and full processed datasets must be gitignored.

---

## File Structure

- Create `backend/pyproject.toml`: backend dependencies, pytest config, package metadata.
- Create `backend/app/main.py`: FastAPI app factory, CORS, router registration.
- Create `backend/app/routers/health.py`: `/health` endpoint.
- Create `backend/app/routers/datasets.py`: dataset metadata endpoint.
- Create `backend/app/routers/experiments.py`: precomputed and live experiment endpoints.
- Create `backend/app/schemas/experiments.py`: request/response Pydantic models shared by routes/services.
- Create `backend/app/services/data_service.py`: load committed sample metadata/results.
- Create `backend/app/services/experiment_service.py`: validate requests and call `backend/mab`.
- Create `backend/mab/algorithms/base.py`: common bandit protocol and `BanditState`.
- Create `backend/mab/algorithms/epsilon_greedy.py`: Epsilon-Greedy policy.
- Create `backend/mab/algorithms/ucb.py`: UCB1 and Sliding-Window UCB policies.
- Create `backend/mab/algorithms/thompson.py`: Gaussian Thompson Sampling policy.
- Create `backend/mab/algorithms/oracle.py`: oracle baseline for known environments.
- Create `backend/mab/environments/base.py`: common pricing environment protocol.
- Create `backend/mab/environments/empirical.py`: empirical reward-sampling environment.
- Create `backend/mab/environments/elasticity.py`: elasticity-based demand environment.
- Create `backend/mab/metrics.py`: cumulative revenue, regret, summaries.
- Create `backend/mab/simulation.py`: run one or more algorithms and return traces.
- Create `backend/pipelines/download_data.py`: UCI download helper.
- Create `backend/pipelines/clean_data.py`: clean UCI or synthetic transactions.
- Create `backend/pipelines/make_sample.py`: create committed sample payloads.
- Create `backend/experiments/run_experiment.py`: CLI for precomputing result JSON.
- Create `backend/tests/`: pytest coverage for algorithms, environments, pipeline fallback, simulation, and API.
- Create `data/samples/catalog.json`: compact product/category metadata.
- Create `data/samples/precomputed_results.json`: committed dashboard-ready results.
- Create `.gitignore`: Python, Node, build output, raw/processed data.
- Create `frontend/package.json`, `frontend/tsconfig.json`, `frontend/vite.config.ts`, `frontend/index.html`.
- Create `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/styles.css`.
- Create `frontend/src/api/client.ts`: API client with `VITE_API_BASE_URL`.
- Create `frontend/src/types.ts`: frontend API type mirrors.
- Create `frontend/src/components/`: tabs, controls, KPI cards, charts, tables.
- Create `frontend/src/pages/Overview.tsx`: executive dashboard.
- Create `frontend/src/pages/Lab.tsx`: interactive simulation lab.
- Replace `README.md`: full project story, setup, commands, and limitations.
- Create `docs/deployment.md`: Vercel + Render deployment instructions.

---

### Task 1: Repository Scaffold And Backend Package

**Files:**
- Create: `.gitignore`
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/mab/__init__.py`
- Create: `backend/mab/algorithms/__init__.py`
- Create: `backend/mab/environments/__init__.py`
- Create: `backend/pipelines/__init__.py`
- Create: `backend/tests/__init__.py`

**Interfaces:**
- Produces: installable backend project where `python -m pytest` runs from `backend/`.
- Produces: import roots `app`, `mab`, and `pipelines`.

- [ ] **Step 1: Add root ignore rules**

Create `.gitignore`:

```gitignore
.worktrees/
.superpowers/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.mypy_cache/
.venv/
venv/
backend/.venv/

node_modules/
dist/
frontend/dist/
frontend/.vite/

data/raw/
data/processed/
backend/experiments/results/

.env
.env.*
!.env.example
```

- [ ] **Step 2: Add backend package config**

Create `backend/pyproject.toml`:

```toml
[project]
name = "dynamic-retail-pricing-mab"
version = "0.1.0"
description = "Dynamic retail pricing with multi-armed bandits"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.116,<1.0",
  "uvicorn[standard]>=0.35,<1.0",
  "pydantic>=2.8,<3.0",
  "pandas>=2.2,<3.0",
  "numpy>=2.0,<3.0",
  "openpyxl>=3.1,<4.0",
  "requests>=2.32,<3.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2,<9.0",
  "httpx>=0.27,<1.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
addopts = "-q"
```

- [ ] **Step 3: Create package markers**

Create empty `__init__.py` files for all package directories listed in this task.

- [ ] **Step 4: Install backend dependencies**

Run:

```powershell
cd backend
python -m pip install -e ".[dev]"
```

Expected: packages install successfully.

- [ ] **Step 5: Verify test command starts clean**

Run:

```powershell
cd backend
python -m pytest
```

Expected: pytest exits with code `5` and prints `no tests ran`, which is acceptable before test files exist.

- [ ] **Step 6: Commit scaffold**

```powershell
git add .gitignore backend
git commit -m "chore: scaffold backend package"
```

---

### Task 2: Bandit Interfaces And Algorithm Tests

**Files:**
- Create: `backend/mab/algorithms/base.py`
- Create: `backend/mab/algorithms/epsilon_greedy.py`
- Create: `backend/mab/algorithms/ucb.py`
- Create: `backend/mab/algorithms/thompson.py`
- Create: `backend/mab/algorithms/oracle.py`
- Create: `backend/tests/test_algorithms.py`

**Interfaces:**
- Produces: `Arm = float`
- Produces: `BanditState(name: str, counts: dict[float, int], values: dict[float, float], total_pulls: int, metadata: dict[str, float])`
- Produces: `BanditPolicy.select_arm() -> float`, `BanditPolicy.update(arm: float, reward: float) -> None`, `BanditPolicy.state() -> BanditState`
- Consumes later: `make_policy(name: str, arms: list[float], seed: int, **params) -> BanditPolicy`

- [ ] **Step 1: Write failing algorithm tests**

Create `backend/tests/test_algorithms.py`:

```python
import math

import pytest

from mab.algorithms.base import make_policy


ALGORITHMS = ["epsilon_greedy", "ucb1", "sliding_window_ucb", "thompson_sampling"]


@pytest.mark.parametrize("name", ALGORITHMS)
def test_policy_selects_valid_arm(name):
    arms = [1.0, 2.0, 3.0]
    policy = make_policy(name, arms=arms, seed=7)

    selected = policy.select_arm()

    assert selected in arms


@pytest.mark.parametrize("name", ALGORITHMS)
def test_policy_updates_counts_and_values(name):
    arms = [1.0, 2.0, 3.0]
    policy = make_policy(name, arms=arms, seed=7)

    arm = policy.select_arm()
    policy.update(arm, 12.5)
    state = policy.state()

    assert state.total_pulls == 1
    assert state.counts[arm] == 1
    assert math.isclose(state.values[arm], 12.5)


def test_epsilon_greedy_exploits_best_observed_arm_when_epsilon_zero():
    policy = make_policy("epsilon_greedy", arms=[1.0, 2.0], seed=3, epsilon=0.0)
    policy.update(1.0, 5.0)
    policy.update(2.0, 9.0)

    assert policy.select_arm() == 2.0


def test_sliding_window_ucb_forgets_old_observations():
    policy = make_policy("sliding_window_ucb", arms=[1.0, 2.0], seed=3, window_size=2)
    policy.update(1.0, 100.0)
    policy.update(2.0, 1.0)
    policy.update(2.0, 1.0)

    state = policy.state()

    assert state.total_pulls == 2
    assert state.counts[1.0] == 0
    assert state.counts[2.0] == 2


def test_oracle_uses_environment_best_arm():
    policy = make_policy("oracle", arms=[1.0, 2.0], seed=1, best_arm=2.0)

    assert policy.select_arm() == 2.0
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
cd backend
python -m pytest tests/test_algorithms.py -q
```

Expected: import failure for missing `mab.algorithms.base`.

- [ ] **Step 3: Implement common interface and factory**

Create `backend/mab/algorithms/base.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

Arm = float


@dataclass(frozen=True)
class BanditState:
    name: str
    counts: dict[Arm, int]
    values: dict[Arm, float]
    total_pulls: int
    metadata: dict[str, float] = field(default_factory=dict)


class BanditPolicy(Protocol):
    name: str
    arms: list[Arm]

    def select_arm(self) -> Arm:
        ...

    def update(self, arm: Arm, reward: float) -> None:
        ...

    def state(self) -> BanditState:
        ...


def make_policy(name: str, arms: list[Arm], seed: int = 0, **params: object) -> BanditPolicy:
    from mab.algorithms.epsilon_greedy import EpsilonGreedy
    from mab.algorithms.oracle import OraclePolicy
    from mab.algorithms.thompson import ThompsonSampling
    from mab.algorithms.ucb import SlidingWindowUCB, UCB1

    if not arms:
        raise ValueError("arms must contain at least one price")

    registry = {
        "epsilon_greedy": EpsilonGreedy,
        "ucb1": UCB1,
        "sliding_window_ucb": SlidingWindowUCB,
        "thompson_sampling": ThompsonSampling,
        "oracle": OraclePolicy,
    }
    try:
        policy_cls = registry[name]
    except KeyError as exc:
        raise ValueError(f"unsupported algorithm: {name}") from exc
    return policy_cls(arms=arms, seed=seed, **params)
```

- [ ] **Step 4: Implement algorithms**

Create focused algorithm files. Core behavior:

```python
# backend/mab/algorithms/epsilon_greedy.py
from __future__ import annotations

import random

from mab.algorithms.base import Arm, BanditState


class EpsilonGreedy:
    name = "epsilon_greedy"

    def __init__(self, arms: list[Arm], seed: int = 0, epsilon: float = 0.1, **_: object) -> None:
        self.arms = list(arms)
        self.epsilon = float(epsilon)
        self._rng = random.Random(seed)
        self._counts = {arm: 0 for arm in self.arms}
        self._values = {arm: 0.0 for arm in self.arms}
        self._total_pulls = 0

    def select_arm(self) -> Arm:
        untried = [arm for arm in self.arms if self._counts[arm] == 0]
        if untried:
            return self._rng.choice(untried)
        if self._rng.random() < self.epsilon:
            return self._rng.choice(self.arms)
        return max(self.arms, key=lambda arm: self._values[arm])

    def update(self, arm: Arm, reward: float) -> None:
        self._total_pulls += 1
        self._counts[arm] += 1
        count = self._counts[arm]
        old = self._values[arm]
        self._values[arm] = old + (reward - old) / count

    def state(self) -> BanditState:
        return BanditState(self.name, dict(self._counts), dict(self._values), self._total_pulls, {"epsilon": self.epsilon})
```

Implement `UCB1` with `value + sqrt(2 * log(total_pulls) / count)`, `SlidingWindowUCB` with a bounded event list of `(arm, reward)`, `ThompsonSampling` with Gaussian samples around empirical means using `1 / sqrt(count)`, and `OraclePolicy` that always returns `best_arm`.

- [ ] **Step 5: Run algorithm tests**

Run:

```powershell
cd backend
python -m pytest tests/test_algorithms.py -q
```

Expected: all tests pass.

- [ ] **Step 6: Commit algorithms**

```powershell
git add backend/mab/algorithms backend/tests/test_algorithms.py
git commit -m "feat: add bandit algorithms"
```

---

### Task 3: Environments, Metrics, And Simulation

**Files:**
- Create: `backend/mab/environments/base.py`
- Create: `backend/mab/environments/empirical.py`
- Create: `backend/mab/environments/elasticity.py`
- Create: `backend/mab/metrics.py`
- Create: `backend/mab/simulation.py`
- Create: `backend/tests/test_environments.py`
- Create: `backend/tests/test_simulation.py`

**Interfaces:**
- Consumes: `make_policy(name, arms, seed, **params)`
- Produces: `PricingEnvironment.pull(arm: float) -> float`
- Produces: `PricingEnvironment.expected_reward(arm: float) -> float`
- Produces: `SimulationRequestConfig`, `SimulationResult`, and `run_simulation(...)`

- [ ] **Step 1: Write failing environment tests**

Create `backend/tests/test_environments.py`:

```python
from mab.environments.elasticity import ElasticityEnvironment
from mab.environments.empirical import EmpiricalArmEnvironment


def test_empirical_environment_samples_known_rewards():
    env = EmpiricalArmEnvironment(rewards_by_arm={1.0: [10.0, 12.0], 2.0: [8.0]}, seed=1)

    reward = env.pull(1.0)

    assert reward in {10.0, 12.0}
    assert env.best_arm() == 1.0


def test_elasticity_environment_rewards_peak_near_reasonable_price():
    env = ElasticityEnvironment(base_price=10.0, base_demand=20.0, elasticity=-1.2, arms=[8.0, 10.0, 12.0], seed=4, noise_scale=0.0)

    rewards = {arm: env.expected_reward(arm) for arm in env.arms}

    assert rewards[12.0] > 0
    assert env.best_arm() in env.arms
```

- [ ] **Step 2: Write failing simulation tests**

Create `backend/tests/test_simulation.py`:

```python
from mab.environments.empirical import EmpiricalArmEnvironment
from mab.simulation import run_simulation


def test_run_simulation_returns_trace_and_summary():
    env = EmpiricalArmEnvironment({1.0: [5.0], 2.0: [10.0]}, seed=2)

    result = run_simulation(
        environment=env,
        algorithms=["epsilon_greedy", "ucb1"],
        horizon=8,
        seed=9,
        parameters={"epsilon_greedy": {"epsilon": 0.1}},
    )

    assert len(result.traces) == 16
    assert {row.algorithm for row in result.summary} == {"epsilon_greedy", "ucb1"}
    assert all(row.cumulative_regret >= 0 for row in result.summary)
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```powershell
cd backend
python -m pytest tests/test_environments.py tests/test_simulation.py -q
```

Expected: import failures for missing environment and simulation modules.

- [ ] **Step 4: Implement environment protocol and classes**

Create `backend/mab/environments/base.py` with a `Protocol` exposing `arms`, `pull`, `expected_reward`, and `best_arm`.

Create `EmpiricalArmEnvironment` that validates non-empty reward lists and samples with `random.Random(seed)`.

Create `ElasticityEnvironment` with:

```python
expected_demand = max(0.0, base_demand * (arm / base_price) ** elasticity)
expected_reward = arm * expected_demand
reward = max(0.0, rng.gauss(expected_reward, expected_reward * noise_scale))
```

- [ ] **Step 5: Implement metrics and simulation**

Create dataclasses:

```python
@dataclass(frozen=True)
class TraceRow:
    step: int
    algorithm: str
    arm: float
    reward: float
    cumulative_reward: float
    cumulative_regret: float


@dataclass(frozen=True)
class SummaryRow:
    algorithm: str
    cumulative_reward: float
    cumulative_regret: float
    best_arm: float
    pulls: int


@dataclass(frozen=True)
class SimulationResult:
    traces: list[TraceRow]
    summary: list[SummaryRow]
    arms: list[float]
```

`run_simulation` creates one environment clone per algorithm when needed, computes `oracle_reward = environment.expected_reward(environment.best_arm())`, updates each policy for `horizon` pulls, and returns trace/summary dataclasses.

- [ ] **Step 6: Run tests**

Run:

```powershell
cd backend
python -m pytest tests/test_environments.py tests/test_simulation.py -q
```

Expected: all tests pass.

- [ ] **Step 7: Commit environments and simulation**

```powershell
git add backend/mab/environments backend/mab/metrics.py backend/mab/simulation.py backend/tests/test_environments.py backend/tests/test_simulation.py
git commit -m "feat: add pricing environments and simulation"
```

---

### Task 4: Data Pipeline, Synthetic Fallback, And Samples

**Files:**
- Create: `backend/pipelines/download_data.py`
- Create: `backend/pipelines/clean_data.py`
- Create: `backend/pipelines/make_sample.py`
- Create: `backend/tests/test_pipeline.py`
- Create: `data/samples/catalog.json`
- Create: `data/samples/precomputed_results.json`

**Interfaces:**
- Produces: `clean_transactions(frame: pandas.DataFrame) -> pandas.DataFrame`
- Produces: `build_synthetic_transactions(seed: int = 0) -> pandas.DataFrame`
- Produces: `build_sample_payload(output_dir: Path) -> None`
- Consumes later: sample JSON loaded by API and frontend fallback.

- [ ] **Step 1: Write failing pipeline tests**

Create `backend/tests/test_pipeline.py`:

```python
import pandas as pd

from pipelines.clean_data import build_synthetic_transactions, clean_transactions, select_sample_products


def test_clean_transactions_removes_returns_and_bad_prices():
    raw = pd.DataFrame(
        [
            {"InvoiceNo": "1", "StockCode": "A", "Description": "MUG", "Quantity": 2, "InvoiceDate": "2011-01-01", "UnitPrice": 3.0, "CustomerID": 1, "Country": "UK"},
            {"InvoiceNo": "C2", "StockCode": "A", "Description": "MUG", "Quantity": -1, "InvoiceDate": "2011-01-02", "UnitPrice": 3.0, "CustomerID": 1, "Country": "UK"},
            {"InvoiceNo": "3", "StockCode": "B", "Description": "BAG", "Quantity": 1, "InvoiceDate": "2011-01-03", "UnitPrice": 0.0, "CustomerID": 2, "Country": "UK"},
        ]
    )

    cleaned = clean_transactions(raw)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["revenue"] == 6.0


def test_synthetic_transactions_have_required_columns():
    frame = build_synthetic_transactions(seed=4)

    assert {"stock_code", "description", "quantity", "unit_price", "invoice_date", "revenue"}.issubset(frame.columns)
    assert len(frame) >= 100


def test_select_sample_products_returns_requested_count():
    frame = build_synthetic_transactions(seed=4)

    selected = select_sample_products(frame, count=3)

    assert len(selected["stock_code"].unique()) == 3
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
cd backend
python -m pytest tests/test_pipeline.py -q
```

Expected: import failure for missing `pipelines.clean_data`.

- [ ] **Step 3: Implement cleaning and synthetic fallback**

Create `clean_transactions` that lowercases canonical column names, filters cancellation invoices beginning with `C`, filters `quantity > 0` and `unit_price > 0`, parses dates, strips missing descriptions, and computes `revenue`.

Create `build_synthetic_transactions` with 5 products, 365 days, product-specific base prices, elastic demand, and random seasonality. Return columns `stock_code`, `description`, `quantity`, `unit_price`, `invoice_date`, `country`, `revenue`.

- [ ] **Step 4: Implement downloader with graceful failure**

Create `backend/pipelines/download_data.py` with `download_uci_online_retail(raw_dir: Path) -> Path`. It first returns an existing file from `data/raw/`, then tries direct UCI download using `requests`, then raises a clear `RuntimeError` with instruction to use synthetic fallback.

- [ ] **Step 5: Implement sample builder**

Create `build_sample_payload(output_dir: Path) -> None` that writes:

`catalog.json`:

```json
{
  "source": "UCI Online Retail or synthetic fallback",
  "products": [
    {"id": "SYN-001", "name": "Ceramic Mug", "observations": 365}
  ]
}
```

`precomputed_results.json` with at least one product, both environment types, algorithm summaries, and trace arrays from `run_simulation`.

- [ ] **Step 6: Generate committed sample files**

Run:

```powershell
cd backend
python -m pipelines.make_sample --output ..\data\samples
```

Expected: `data/samples/catalog.json` and `data/samples/precomputed_results.json` exist and are compact.

- [ ] **Step 7: Run pipeline tests**

Run:

```powershell
cd backend
python -m pytest tests/test_pipeline.py -q
```

Expected: all tests pass.

- [ ] **Step 8: Commit pipeline and sample data**

```powershell
git add backend/pipelines backend/tests/test_pipeline.py data/samples
git commit -m "feat: add retail data pipeline and samples"
```

---

### Task 5: Experiment Runner

**Files:**
- Create: `backend/experiments/run_experiment.py`
- Create: `backend/tests/test_experiment_runner.py`

**Interfaces:**
- Consumes: `run_simulation`, `EmpiricalArmEnvironment`, `ElasticityEnvironment`, sample data.
- Produces: CLI command `python -m experiments.run_experiment --output ../data/samples/precomputed_results.json`.

- [ ] **Step 1: Write failing CLI helper test**

Create `backend/tests/test_experiment_runner.py`:

```python
from pathlib import Path

from experiments.run_experiment import build_precomputed_results, write_results


def test_build_precomputed_results_contains_overview_and_lab_defaults(tmp_path: Path):
    payload = build_precomputed_results(seed=5, horizon=25)

    assert "overview" in payload
    assert "lab_defaults" in payload
    assert payload["overview"]["summaries"]
    assert payload["overview"]["traces"]


def test_write_results_creates_json(tmp_path: Path):
    output = tmp_path / "precomputed_results.json"

    write_results(output, {"overview": {"summaries": [], "traces": []}})

    assert output.exists()
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
cd backend
python -m pytest tests/test_experiment_runner.py -q
```

Expected: import failure for missing `experiments.run_experiment`.

- [ ] **Step 3: Implement experiment runner**

Create `build_precomputed_results(seed: int = 42, horizon: int = 200) -> dict[str, object]` that runs all v1 algorithms on empirical and elasticity sample environments and returns JSON-serializable dictionaries.

Create `write_results(output: Path, payload: dict[str, object]) -> None` that creates parent directories and writes indented JSON.

Add CLI args: `--output`, `--seed`, `--horizon`.

- [ ] **Step 4: Run runner tests**

Run:

```powershell
cd backend
python -m pytest tests/test_experiment_runner.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Refresh precomputed sample results**

Run:

```powershell
cd backend
python -m experiments.run_experiment --output ..\data\samples\precomputed_results.json --seed 42 --horizon 200
```

Expected: JSON file is updated with overview summaries and traces.

- [ ] **Step 6: Commit experiment runner**

```powershell
git add backend/experiments backend/tests/test_experiment_runner.py data/samples/precomputed_results.json
git commit -m "feat: add experiment runner"
```

---

### Task 6: FastAPI Schemas, Services, And Routes

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/routers/health.py`
- Create: `backend/app/routers/datasets.py`
- Create: `backend/app/routers/experiments.py`
- Create: `backend/app/schemas/experiments.py`
- Create: `backend/app/services/data_service.py`
- Create: `backend/app/services/experiment_service.py`
- Create: `backend/tests/test_api.py`

**Interfaces:**
- Consumes: `data/samples/catalog.json`, `data/samples/precomputed_results.json`, `run_simulation`.
- Produces: `GET /health`, `GET /datasets`, `GET /experiments/precomputed`, `POST /experiments/run`.

- [ ] **Step 1: Write failing API tests**

Create `backend/tests/test_api.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_datasets_endpoint_returns_products():
    response = client.get("/datasets")

    assert response.status_code == 200
    assert response.json()["products"]


def test_precomputed_endpoint_returns_overview():
    response = client.get("/experiments/precomputed")

    assert response.status_code == 200
    assert "overview" in response.json()


def test_run_experiment_endpoint_returns_summary_and_traces():
    response = client.post(
        "/experiments/run",
        json={
            "environment": "elasticity",
            "horizon": 25,
            "seed": 9,
            "algorithms": ["epsilon_greedy", "ucb1"],
            "parameters": {"epsilon_greedy": {"epsilon": 0.1}},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]
    assert payload["traces"]
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
cd backend
python -m pytest tests/test_api.py -q
```

Expected: import failure for missing `app.main`.

- [ ] **Step 3: Implement Pydantic schemas**

Create request schema with fields:

```python
environment: Literal["empirical", "elasticity"]
horizon: int = Field(ge=10, le=1000)
seed: int = Field(ge=0, le=1_000_000)
algorithms: list[Literal["epsilon_greedy", "ucb1", "sliding_window_ucb", "thompson_sampling"]]
parameters: dict[str, dict[str, float | int]] = {}
```

Create response models for trace rows and summary rows.

- [ ] **Step 4: Implement services and routes**

`data_service.py` loads JSON using paths relative to repo root. If sample files are missing, return synthetic in-memory defaults from `build_precomputed_results`.

`experiment_service.py` builds empirical or elasticity environment from sample defaults and calls `run_simulation`.

Register routers in `app/main.py` and configure CORS from `FRONTEND_ORIGINS` env var with local defaults `http://localhost:5173` and `http://127.0.0.1:5173`.

- [ ] **Step 5: Run API tests**

Run:

```powershell
cd backend
python -m pytest tests/test_api.py -q
```

Expected: all tests pass.

- [ ] **Step 6: Smoke test local API**

Run:

```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another shell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected: `status : ok`.

- [ ] **Step 7: Commit API**

```powershell
git add backend/app backend/tests/test_api.py
git commit -m "feat: add FastAPI experiment API"
```

---

### Task 7: Frontend Scaffold, API Client, And Base Layout

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/types.ts`
- Create: `frontend/src/styles.css`
- Create: `frontend/src/components/Tabs.tsx`

**Interfaces:**
- Consumes: FastAPI endpoints.
- Produces: `fetchDatasets()`, `fetchPrecomputed()`, `runExperiment(request)`.
- Produces: app shell with `Overview` and `Lab` tabs backed by sample fixtures when the API is unavailable.

- [ ] **Step 1: Add frontend package config**

Create `frontend/package.json`:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@vitejs/plugin-react": "^5.0.0",
    "vite": "^7.0.0",
    "typescript": "^5.5.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "recharts": "^2.12.7",
    "lucide-react": "^0.468.0"
  },
  "devDependencies": {}
}
```

- [ ] **Step 2: Create TypeScript/Vite files**

Use standard React JSX config with strict mode enabled. `vite.config.ts` uses `react()` plugin.

- [ ] **Step 3: Create API types**

Create `frontend/src/types.ts` with `DatasetCatalog`, `ExperimentRequest`, `TraceRow`, `SummaryRow`, and `ExperimentResponse`. Match backend JSON field names exactly.

- [ ] **Step 4: Create API client**

Create `frontend/src/api/client.ts`:

```ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}
```

Export `fetchDatasets`, `fetchPrecomputed`, and `runExperiment`.

- [ ] **Step 5: Create app shell**

`App.tsx` holds `activeTab` state and renders tab buttons, header, and active page. Header title: `Dynamic Retail Pricing Lab`.

- [ ] **Step 6: Install and build frontend**

Run:

```powershell
cd frontend
npm install
npm run build
```

Expected: build succeeds and emits `frontend/dist`.

- [ ] **Step 7: Commit frontend scaffold**

```powershell
git add frontend
git commit -m "feat: scaffold React dashboard"
```

---

### Task 8: Overview Dashboard

**Files:**
- Create: `frontend/src/pages/Overview.tsx`
- Create: `frontend/src/components/KpiCard.tsx`
- Create: `frontend/src/components/StrategyTable.tsx`
- Create: `frontend/src/charts/RevenueRegretChart.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles.css`

**Interfaces:**
- Consumes: `fetchPrecomputed()`.
- Produces: recruiter-friendly dashboard with KPI strip, chart, table, narrative, and dataset card.

- [ ] **Step 1: Build chart component**

Create `RevenueRegretChart.tsx` using Recharts `ResponsiveContainer`, `LineChart`, `Line`, `XAxis`, `YAxis`, `Tooltip`, and `Legend`. It accepts:

```ts
type Props = {
  traces: TraceRow[];
  metric: "cumulative_reward" | "cumulative_regret";
};
```

Transform trace rows into step-indexed series grouped by algorithm.

- [ ] **Step 2: Build KPI card and strategy table**

`KpiCard` accepts `label`, `value`, and `detail`. `StrategyTable` accepts `summary: SummaryRow[]` and sorts by highest `cumulative_reward`.

- [ ] **Step 3: Build Overview page**

`Overview.tsx` fetches precomputed results on mount, handles loading/error states, computes winner, revenue lift versus Epsilon-Greedy, and regret reduction versus Epsilon-Greedy.

Narrative copy must include:

```text
Counterfactual demand is simulated from historical retail transactions, so the dashboard demonstrates policy behavior rather than causal proof.
```

- [ ] **Step 4: Style dashboard**

Use restrained analytics styling:

- dense but readable layout
- no hero landing page
- no card-within-card nesting
- max card radius `8px`
- charts keep stable minimum heights
- colors use neutral background plus distinct algorithm colors, not one-hue palette

- [ ] **Step 5: Build frontend**

Run:

```powershell
cd frontend
npm run build
```

Expected: build succeeds.

- [ ] **Step 6: Commit Overview**

```powershell
git add frontend/src
git commit -m "feat: add overview dashboard"
```

---

### Task 9: Interactive Lab

**Files:**
- Create: `frontend/src/pages/Lab.tsx`
- Create: `frontend/src/components/LabControls.tsx`
- Create: `frontend/src/charts/ArmShareChart.tsx`
- Create: `frontend/src/charts/RewardTrendChart.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles.css`

**Interfaces:**
- Consumes: `runExperiment(request)`.
- Produces: interactive controls and charts for live simulation.

- [ ] **Step 1: Build lab controls**

`LabControls` exposes:

```ts
type LabSettings = {
  environment: "empirical" | "elasticity";
  horizon: number;
  seed: number;
  algorithms: string[];
  epsilon: number;
  windowSize: number;
};
```

Controls include segmented environment switch, numeric inputs for horizon/seed/window, epsilon slider, and algorithm checkboxes.

- [ ] **Step 2: Build arm share chart**

`ArmShareChart` groups traces by `algorithm` and `arm`, computes percentages, and renders a stacked bar chart.

- [ ] **Step 3: Build reward trend chart**

`RewardTrendChart` renders rolling average reward per algorithm. Use a fixed 10-step rolling window for v1.

- [ ] **Step 4: Build Lab page**

`Lab.tsx` initializes defaults:

```ts
{
  environment: "elasticity",
  horizon: 200,
  seed: 42,
  algorithms: ["epsilon_greedy", "ucb1", "sliding_window_ucb", "thompson_sampling"],
  epsilon: 0.1,
  windowSize: 50
}
```

On Run, call `/experiments/run`, show loading state, render cumulative revenue, cumulative regret, arm share, reward trend, and winner summary.

- [ ] **Step 5: Build frontend**

Run:

```powershell
cd frontend
npm run build
```

Expected: build succeeds.

- [ ] **Step 6: Commit Lab**

```powershell
git add frontend/src
git commit -m "feat: add interactive lab"
```

---

### Task 10: README And Deployment Docs

**Files:**
- Modify: `README.md`
- Create: `docs/deployment.md`

**Interfaces:**
- Consumes: verified local commands from earlier tasks.
- Produces: user-facing project explanation and deployment instructions.

- [ ] **Step 1: Replace README**

README sections:

- Project title and one-paragraph value proposition.
- Screenshots section with explicit note: `Screenshots will be added after local browser verification.`
- What makes it unique: real retail data, hybrid simulator, algorithm comparison, polished lab.
- Architecture diagram in text.
- Algorithms explained briefly.
- Data limitations and UCI citation.
- Local setup commands for backend and frontend.
- Experiment commands.
- Test commands.
- Deployment overview.

- [ ] **Step 2: Add deployment guide**

`docs/deployment.md` includes:

- Render backend service setup from `backend`.
- Render start command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Vercel frontend setup from `frontend`.
- Vercel env var: `VITE_API_BASE_URL`.
- Backend env var: `FRONTEND_ORIGINS`.
- Post-deploy checks: `/health`, `/datasets`, Overview load, Lab run.

- [ ] **Step 3: Commit docs**

```powershell
git add README.md docs/deployment.md
git commit -m "docs: add setup and deployment guide"
```

---

### Task 11: Local Verification And Polish

**Files:**
- Modify only files needed to fix verification failures.

**Interfaces:**
- Consumes: all prior tasks.
- Produces: final verified local project and clear deployment readiness note.

- [ ] **Step 1: Run backend tests**

Run:

```powershell
cd backend
python -m pytest -q
```

Expected: all backend tests pass.

- [ ] **Step 2: Run frontend build**

Run:

```powershell
cd frontend
npm run build
```

Expected: build succeeds.

- [ ] **Step 3: Start backend**

Run:

```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Expected: server listens on `http://127.0.0.1:8000`.

- [ ] **Step 4: Start frontend**

Run:

```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Expected: Vite serves `http://127.0.0.1:5173`.

- [ ] **Step 5: Browser verify**

Use Playwright or manual browser:

- load `http://127.0.0.1:5173`
- Overview KPI cards render
- revenue/regret chart renders
- strategy table has all algorithms
- switch to Lab
- run one `elasticity` experiment with horizon `50`
- charts update
- browser console has no relevant runtime errors

- [ ] **Step 6: Fix verification failures**

For each failure, identify root cause, make smallest focused patch, rerun the failing command, then rerun full backend/frontend verification.

- [ ] **Step 7: Commit verification fixes**

If fixes were needed:

```powershell
git add <changed-files>
git commit -m "fix: stabilize local verification"
```

If no fixes were needed, do not create an empty commit.

---

### Advisor-Required Verification Addendum

Apply these checks while executing the tasks above. Add the exact tests into the nearest task file named below.

**Task 3 additions: simulation determinism and numeric sanity**

Add to `backend/tests/test_simulation.py`:

```python
def test_run_simulation_is_deterministic_for_same_seed():
    env_a = EmpiricalArmEnvironment({1.0: [5.0], 2.0: [10.0]}, seed=2)
    env_b = EmpiricalArmEnvironment({1.0: [5.0], 2.0: [10.0]}, seed=2)

    result_a = run_simulation(env_a, ["epsilon_greedy", "ucb1"], horizon=12, seed=9, parameters={})
    result_b = run_simulation(env_b, ["epsilon_greedy", "ucb1"], horizon=12, seed=9, parameters={})

    assert result_a.traces == result_b.traces


def test_oracle_expected_reward_is_at_least_each_arm_expected_reward():
    env = EmpiricalArmEnvironment({1.0: [5.0], 2.0: [10.0]}, seed=2)
    oracle_reward = env.expected_reward(env.best_arm())

    assert all(oracle_reward >= env.expected_reward(arm) for arm in env.arms)
```

**Task 4 additions: committed sample is deploy-safe**

Add to `backend/tests/test_pipeline.py`:

```python
def test_sample_payload_files_are_small_and_network_free(tmp_path):
    from pipelines.make_sample import build_sample_payload

    build_sample_payload(tmp_path)

    catalog = tmp_path / "catalog.json"
    results = tmp_path / "precomputed_results.json"
    assert catalog.exists()
    assert results.exists()
    assert catalog.stat().st_size < 100_000
    assert results.stat().st_size < 2_000_000
```

**Task 6 additions: API chart contract and CORS**

Add to `backend/tests/test_api.py`:

```python
def test_run_experiment_response_has_consistent_chart_arrays():
    response = client.post(
        "/experiments/run",
        json={
            "environment": "empirical",
            "horizon": 10,
            "seed": 5,
            "algorithms": ["epsilon_greedy", "ucb1", "sliding_window_ucb"],
            "parameters": {},
        },
    )

    payload = response.json()
    assert response.status_code == 200
    assert len(payload["traces"]) == 30
    assert len(payload["summary"]) == 3
    assert {row["algorithm"] for row in payload["summary"]} == {"epsilon_greedy", "ucb1", "sliding_window_ucb"}


def test_cors_allows_local_frontend_origin():
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code in {200, 204}
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
```

**Task 7 additions: frontend fixture fallback**

Create `frontend/src/api/fixtures.ts` with compact `catalogFixture` and `precomputedFixture` objects matching `DatasetCatalog` and the precomputed response type. Include one product, two algorithms, and ten trace points so Overview can render before the live API is available.

**Task 11 additions: fresh sample-mode smoke**

Run from a clean working tree with no `data/raw/` or `data/processed/` directories:

```powershell
cd backend
python -c "from app.main import app; print(app.title)"
python -m pytest -q
cd ..\frontend
npm run build
```

Expected: backend imports, backend tests pass, frontend builds, and no command requires network data download.

Deployment configuration check:

- `VITE_API_BASE_URL` is set before Vercel build.
- `FRONTEND_ORIGINS` supports localhost and exact deployed Vercel URL.
- Render start command uses `$PORT`.
- `/health` is documented as Render cold-start check.
---

## Self-Review

Spec coverage:

- Research engine: Tasks 2, 3, 5.
- Real/synthetic data: Task 4.
- FastAPI backend: Task 6.
- React/Vite dashboard: Tasks 7, 8, 9.
- Docs/deployment: Task 10.
- Verification: Task 11.

Red flag scan:

- No deferred decisions remain for v1.
- No task depends on full UCI download during app startup.
- No task asks implementers to claim causal pricing proof.

Type consistency:

- Backend simulation produces `TraceRow`, `SummaryRow`, and `SimulationResult`.
- API schemas mirror those fields.
- Frontend `types.ts` mirrors API JSON field names.

