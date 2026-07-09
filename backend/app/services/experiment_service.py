from __future__ import annotations

from dataclasses import asdict

from experiments.run_experiment import (
    _build_elasticity_environment,
    _build_empirical_environment,
    _select_sample_product,
    _serialize_row,
)
from mab.simulation import run_simulation

from app.schemas.experiments import SimulationRequest
from app.services.data_service import load_dataset_catalog


def run_requested_experiment(request: SimulationRequest) -> dict[str, object]:
    catalog = load_dataset_catalog()
    source = str(catalog.get("source", "synthetic_fallback"))
    sample_product = _select_sample_product(catalog)

    if request.environment == "empirical":
        environment = _build_empirical_environment(sample_product, seed=request.seed)
    else:
        environment = _build_elasticity_environment(sample_product, seed=request.seed)

    result = run_simulation(
        environment=environment,
        algorithms=list(request.algorithms),
        horizon=request.horizon,
        seed=request.seed,
        parameters=request.parameters,
    )

    return {
        "source": source,
        "sample_product": {
            "id": sample_product["id"],
            "name": sample_product["name"],
            "observations": sample_product["observations"],
            "price_arms": sample_product["price_arms"],
            "environment_source": sample_product["environment_source"],
        },
        "summary": [
            _serialize_row(asdict(row), environment=request.environment) for row in result.summary
        ],
        "traces": [_serialize_row(asdict(row), environment=request.environment) for row in result.traces],
    }
