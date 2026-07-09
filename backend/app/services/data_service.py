from __future__ import annotations

import json
from pathlib import Path

from experiments.run_experiment import build_precomputed_results


_REPO_ROOT = Path(__file__).resolve().parents[3]
_SAMPLES_DIR = _REPO_ROOT / "data" / "samples"
_CATALOG_PATH = _SAMPLES_DIR / "catalog.json"
_PRECOMPUTED_PATH = _SAMPLES_DIR / "precomputed_results.json"


def load_dataset_catalog() -> dict[str, object]:
    if _CATALOG_PATH.exists():
        payload = _read_json(_CATALOG_PATH)
        if isinstance(payload, dict):
            return payload

    fallback = build_precomputed_results()
    return {
        "source": str(fallback.get("source", "synthetic_fallback")),
        "products": [fallback["sample_product"]],
    }


def load_precomputed_results() -> dict[str, object]:
    if _PRECOMPUTED_PATH.exists():
        payload = _read_json(_PRECOMPUTED_PATH)
        if isinstance(payload, dict):
            return payload

    return build_precomputed_results()


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))
