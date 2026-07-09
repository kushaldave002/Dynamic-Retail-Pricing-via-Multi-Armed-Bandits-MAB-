from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from mab.environments.elasticity import ElasticityEnvironment
from mab.environments.empirical import EmpiricalArmEnvironment
from mab.simulation import run_simulation
from pipelines.clean_data import build_synthetic_transactions, select_sample_products

_SAMPLE_ALGORITHMS = ["epsilon_greedy", "ucb1", "oracle"]


def build_sample_payload(output_dir: Path) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    transactions = build_synthetic_transactions(seed=0)
    sample_products = select_sample_products(transactions, count=1)
    catalog_products: list[dict[str, object]] = []
    result_products: list[dict[str, object]] = []

    for product in _product_payloads(sample_products):
        catalog_products.append(
            {
                "id": product["id"],
                "name": product["name"],
                "observations": product["observations"],
            }
        )
        result_products.append(product)

    catalog = {
        "source": "UCI Online Retail or synthetic fallback",
        "products": catalog_products,
    }
    precomputed_results = {"products": result_products}

    (output_dir / "catalog.json").write_text(
        json.dumps(catalog, separators=(",", ":")),
        encoding="utf-8",
    )
    (output_dir / "precomputed_results.json").write_text(
        json.dumps(precomputed_results, separators=(",", ":")),
        encoding="utf-8",
    )


def _product_payloads(frame):
    for stock_code, product_frame in frame.groupby("stock_code", sort=True):
        product_frame = product_frame.sort_values("invoice_date").reset_index(drop=True)
        price_rewards = (
            product_frame.groupby("unit_price")["revenue"]
            .apply(lambda series: [round(float(value), 2) for value in series.tolist()])
            .to_dict()
        )
        price_arms = sorted(float(arm) for arm in price_rewards)
        reference_row = product_frame.iloc[0]
        observations = int(len(product_frame))
        base_price = float(product_frame["unit_price"].median())
        mean_quantity = float(product_frame["quantity"].mean())
        best_price = float(product_frame.groupby("unit_price")["revenue"].mean().idxmax())
        elasticity = -1.2 if best_price >= base_price else -0.9

        empirical_result = run_simulation(
            environment=EmpiricalArmEnvironment(price_rewards, seed=7),
            algorithms=_SAMPLE_ALGORITHMS,
            horizon=min(16, observations),
            seed=13,
            parameters={"epsilon_greedy": {"epsilon": 0.1}},
        )
        elasticity_result = run_simulation(
            environment=ElasticityEnvironment(
                base_price=base_price,
                base_demand=max(1.0, mean_quantity),
                elasticity=elasticity,
                arms=price_arms,
                seed=11,
                noise_scale=0.05,
            ),
            algorithms=_SAMPLE_ALGORITHMS,
            horizon=16,
            seed=17,
            parameters={"epsilon_greedy": {"epsilon": 0.1}},
        )

        yield {
            "id": stock_code,
            "name": str(reference_row["description"]),
            "observations": observations,
            "environments": {
                "empirical": _serialize_result(empirical_result),
                "elasticity": _serialize_result(elasticity_result),
            },
        }


def _serialize_result(result) -> dict[str, object]:
    return {
        "arms": [_round_float(arm) for arm in result.arms],
        "summary": [_normalize_row(asdict(row)) for row in result.summary],
        "traces": [_normalize_row(asdict(row)) for row in result.traces],
    }


def _normalize_row(row: dict[str, object]) -> dict[str, object]:
    normalized: dict[str, object] = {}
    for key, value in row.items():
        normalized[key] = _round_float(value) if isinstance(value, float) else value
    return normalized


def _round_float(value: float) -> float:
    return round(float(value), 3)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build sample payloads for frontend fallback.")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    build_sample_payload(args.output)


if __name__ == "__main__":
    main()
