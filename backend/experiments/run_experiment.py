from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from mab.environments.elasticity import ElasticityEnvironment
from mab.environments.empirical import EmpiricalArmEnvironment
from mab.simulation import run_simulation

_V1_ALGORITHMS = [
    "epsilon_greedy",
    "ucb1",
    "sliding_window_ucb",
    "thompson_sampling",
    "oracle",
]

_LAB_DEFAULT_ALGORITHMS = [
    "epsilon_greedy",
    "ucb1",
    "sliding_window_ucb",
    "thompson_sampling",
]

_DEFAULT_EPSILON = 0.1
_DEFAULT_WINDOW_SIZE = 50
_CATALOG_PATH = Path(__file__).resolve().parents[2] / "data" / "samples" / "catalog.json"


def build_precomputed_results(seed: int = 42, horizon: int = 200) -> dict[str, object]:
    sample_catalog = _load_sample_catalog()
    sample_source = str(sample_catalog.get("source", "synthetic_fallback"))
    sample_product = _select_sample_product(sample_catalog)

    empirical_environment = _build_empirical_environment(sample_product, seed=seed)
    elasticity_environment = _build_elasticity_environment(sample_product, seed=seed)

    empirical_result = run_simulation(
        environment=empirical_environment,
        algorithms=_V1_ALGORITHMS,
        horizon=horizon,
        seed=seed,
        parameters={
            "epsilon_greedy": {"epsilon": _DEFAULT_EPSILON},
            "sliding_window_ucb": {"window_size": _DEFAULT_WINDOW_SIZE},
        },
    )
    elasticity_result = run_simulation(
        environment=elasticity_environment,
        algorithms=_V1_ALGORITHMS,
        horizon=horizon,
        seed=seed,
        parameters={
            "epsilon_greedy": {"epsilon": _DEFAULT_EPSILON},
            "sliding_window_ucb": {"window_size": _DEFAULT_WINDOW_SIZE},
        },
    )

    reward_row_count = sum(len(rewards) for rewards in _rewards_by_arm(sample_product).values())

    return {
        "source": sample_source,
        "sample_product": {
            "id": sample_product["id"],
            "name": sample_product["name"],
            "observations": sample_product["observations"],
            "price_arms": sample_product["price_arms"],
            "reward_row_count": reward_row_count,
            "environment_source": sample_product["environment_source"],
        },
        "overview": {
            "summaries": [
                *(
                    _serialize_row(asdict(summary), environment="empirical")
                    for summary in empirical_result.summary
                ),
                *(
                    _serialize_row(asdict(summary), environment="elasticity")
                    for summary in elasticity_result.summary
                ),
            ],
            "traces": [
                *(
                    _serialize_row(asdict(trace), environment="empirical")
                    for trace in empirical_result.traces
                ),
                *(
                    _serialize_row(asdict(trace), environment="elasticity")
                    for trace in elasticity_result.traces
                ),
            ],
        },
        "lab_defaults": {
            "environment": "elasticity",
            "horizon": 200,
            "seed": 42,
            "algorithms": list(_LAB_DEFAULT_ALGORITHMS),
            "epsilon": _DEFAULT_EPSILON,
            "windowSize": _DEFAULT_WINDOW_SIZE,
            "sample_source": sample_source,
        },
    }


def write_results(output: Path, payload: dict[str, object]) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _build_empirical_environment(sample_product: dict[str, object], *, seed: int) -> EmpiricalArmEnvironment:
    return EmpiricalArmEnvironment(rewards_by_arm=_rewards_by_arm(sample_product), seed=seed)


def _build_elasticity_environment(sample_product: dict[str, object], *, seed: int) -> ElasticityEnvironment:
    model = sample_product["elasticity_model"]
    return ElasticityEnvironment(
        base_price=float(model["base_price"]),
        base_demand=float(model["base_demand"]),
        elasticity=float(model["elasticity"]),
        arms=_coerce_arms(sample_product),
        seed=seed,
        noise_scale=float(model.get("noise_scale", 0.05)),
    )


def _load_sample_catalog() -> dict[str, object]:
    if not _CATALOG_PATH.exists():
        return _default_sample_catalog()

    payload = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return _default_sample_catalog()

    return {
        "source": payload.get("source", "synthetic_fallback"),
        "products": payload.get("products", []),
    }


def _select_sample_product(sample_catalog: dict[str, object]) -> dict[str, object]:
    products = sample_catalog.get("products")
    if isinstance(products, list):
        for product in products:
            normalized = _normalize_sample_product(product)
            if normalized is not None:
                return normalized
    return _default_sample_product()


def _normalize_sample_product(product: object) -> dict[str, object] | None:
    if not isinstance(product, dict):
        return None

    try:
        price_arms = _coerce_arms(product)
        empirical_rewards = [
            {"arm": arm, "rewards": rewards}
            for arm, rewards in sorted(_rewards_by_arm(product).items())
        ]
        model = product["elasticity_model"]
        normalized_model = {
            "base_price": round(float(model["base_price"]), 3),
            "base_demand": round(float(model["base_demand"]), 3),
            "elasticity": round(float(model["elasticity"]), 3),
            "noise_scale": round(float(model.get("noise_scale", 0.05)), 3),
        }
    except (KeyError, TypeError, ValueError):
        return None

    return {
        "id": str(product.get("id", "SYN-005")),
        "name": str(product.get("name", "Wool Throw")),
        "observations": int(product.get("observations", sum(len(row["rewards"]) for row in empirical_rewards))),
        "price_arms": price_arms,
        "empirical_rewards": empirical_rewards,
        "elasticity_model": normalized_model,
        "environment_source": "sample_catalog",
    }


def _coerce_arms(sample_product: dict[str, object]) -> list[float]:
    arms = sample_product.get("price_arms")
    if isinstance(arms, list) and arms:
        return [round(float(arm), 3) for arm in arms]

    reward_rows = sample_product.get("empirical_rewards")
    if isinstance(reward_rows, list) and reward_rows:
        return [round(float(row["arm"]), 3) for row in reward_rows]

    raise ValueError("sample product is missing price arms")


def _rewards_by_arm(sample_product: dict[str, object]) -> dict[float, list[float]]:
    reward_rows = sample_product.get("empirical_rewards")
    if not isinstance(reward_rows, list) or not reward_rows:
        raise ValueError("sample product is missing empirical reward rows")

    rewards_by_arm: dict[float, list[float]] = {}
    for row in reward_rows:
        if not isinstance(row, dict):
            raise ValueError("empirical reward row must be an object")
        arm = round(float(row["arm"]), 3)
        rewards = row.get("rewards")
        if not isinstance(rewards, list) or not rewards:
            raise ValueError("each empirical reward row must include rewards")
        rewards_by_arm[arm] = [round(float(reward), 3) for reward in rewards]

    return rewards_by_arm


def _default_sample_catalog() -> dict[str, object]:
    return {
        "source": "synthetic_fallback",
        "products": [_default_sample_product()],
    }


def _default_sample_product() -> dict[str, object]:
    return {
        "id": "SYN-005",
        "name": "Wool Throw",
        "observations": 365,
        "price_arms": [35.1, 37.05, 39.0, 40.95, 42.9],
        "empirical_rewards": [
            {"arm": 35.1, "rewards": [245.7, 261.0, 271.8, 255.6]},
            {"arm": 37.05, "rewards": [296.4, 289.8, 282.6, 274.2]},
            {"arm": 39.0, "rewards": [273.0, 327.6, 300.3, 286.65]},
            {"arm": 40.95, "rewards": [327.6, 300.3, 245.7, 286.65]},
            {"arm": 42.9, "rewards": [257.4, 300.3, 343.2, 214.5]},
        ],
        "elasticity_model": {
            "base_price": 37.05,
            "base_demand": 8.5,
            "elasticity": -1.05,
            "noise_scale": 0.05,
        },
        "environment_source": "synthetic_fallback_generated",
    }


def _serialize_row(row: dict[str, object], *, environment: str) -> dict[str, object]:
    serialized = {"environment": environment}
    for key, value in row.items():
        serialized[key] = _normalize_value(value)
    return serialized


def _normalize_value(value: object) -> object:
    if isinstance(value, float):
        return round(value, 3)
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _normalize_value(item) for key, item in value.items()}
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Build precomputed MAB experiment results.")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--horizon", type=int, default=200)
    args = parser.parse_args()

    payload = build_precomputed_results(seed=args.seed, horizon=args.horizon)
    write_results(args.output, payload)


if __name__ == "__main__":
    main()
