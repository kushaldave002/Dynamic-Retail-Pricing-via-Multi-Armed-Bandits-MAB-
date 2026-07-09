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


def build_precomputed_results(seed: int = 42, horizon: int = 200) -> dict[str, object]:
    sample_catalog = _load_sample_catalog()
    sample_source = str(sample_catalog.get("source", "synthetic_fallback"))
    sample_product = sample_catalog["products"][0] if sample_catalog.get("products") else _default_sample_product()

    empirical_environment = _build_empirical_environment(seed=seed)
    elasticity_environment = _build_elasticity_environment(seed=seed)

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

    return {
        "source": sample_source,
        "sample_product": {
            "id": sample_product["id"],
            "name": sample_product["name"],
            "observations": sample_product["observations"],
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


def _build_empirical_environment(*, seed: int) -> EmpiricalArmEnvironment:
    return EmpiricalArmEnvironment(
        rewards_by_arm={
            35.1: [245.7, 261.0, 271.8, 255.6],
            37.05: [296.4, 289.8, 282.6, 274.2],
            39.0: [273.0, 327.6, 300.3, 286.65],
            40.95: [327.6, 300.3, 245.7, 286.65],
            42.9: [257.4, 300.3, 343.2, 214.5],
        },
        seed=seed,
    )


def _build_elasticity_environment(*, seed: int) -> ElasticityEnvironment:
    return ElasticityEnvironment(
        base_price=37.05,
        base_demand=8.5,
        elasticity=-1.05,
        arms=[35.1, 37.05, 39.0, 40.95, 42.9],
        seed=seed,
        noise_scale=0.05,
    )


def _load_sample_catalog() -> dict[str, object]:
    catalog_path = Path(__file__).resolve().parents[2] / "data" / "samples" / "catalog.json"
    if not catalog_path.exists():
        return {
            "source": "synthetic_fallback",
            "products": [_default_sample_product()],
        }

    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {
            "source": "synthetic_fallback",
            "products": [_default_sample_product()],
        }

    products = payload.get("products")
    if not isinstance(products, list) or not products:
        payload["products"] = [_default_sample_product()]
    return payload


def _default_sample_product() -> dict[str, object]:
    return {
        "id": "SYN-005",
        "name": "Wool Throw",
        "observations": 365,
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
