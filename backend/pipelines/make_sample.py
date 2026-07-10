from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from pipelines.clean_data import (
    build_synthetic_transactions,
    clean_transactions,
    select_sample_products,
)
from pipelines.download_data import download_uci_online_retail, find_local_uci_online_retail

_DEFAULT_RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"


def build_sample_payload(
    output_dir: Path,
    raw_dir: Path | None = None,
    allow_download: bool = False,
) -> None:
    """Write catalog.json only. precomputed_results.json is owned by experiments.run_experiment,
    which reads catalog.json produced here — see docs/deployment.md for the regeneration order."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    transactions, source = _resolve_sample_transactions(raw_dir=raw_dir, allow_download=allow_download)
    sample_products = select_sample_products(transactions, count=1)
    catalog_products = [
        {
            "id": product["id"],
            "name": product["name"],
            "observations": product["observations"],
            "price_arms": product["price_arms"],
            "empirical_rewards": product["empirical_rewards"],
            "elasticity_model": product["elasticity_model"],
        }
        for product in _product_payloads(sample_products)
    ]

    catalog = {
        "source": source,
        "products": catalog_products,
    }

    (output_dir / "catalog.json").write_text(
        json.dumps(catalog, separators=(",", ":")),
        encoding="utf-8",
    )


def _resolve_sample_transactions(
    raw_dir: Path | None,
    allow_download: bool,
) -> tuple[pd.DataFrame, str]:
    resolved_raw_dir = Path(raw_dir) if raw_dir is not None else _DEFAULT_RAW_DIR
    local_path = find_local_uci_online_retail(resolved_raw_dir)
    if local_path is not None:
        return _load_and_clean_transactions(local_path), "uci_online_retail_local"

    if allow_download:
        try:
            downloaded_path = download_uci_online_retail(resolved_raw_dir)
        except RuntimeError:
            pass
        else:
            return _load_and_clean_transactions(downloaded_path), "uci_online_retail_downloaded"

    return build_synthetic_transactions(seed=0), "synthetic_fallback"


def _load_and_clean_transactions(raw_path: Path) -> pd.DataFrame:
    frame = _read_raw_transactions(raw_path)
    cleaned = clean_transactions(frame)
    if cleaned.empty:
        raise RuntimeError(f"No usable transactions found in {raw_path}")
    return cleaned


def _read_raw_transactions(raw_path: Path) -> pd.DataFrame:
    suffix = raw_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(raw_path)
    if suffix == ".tsv":
        return pd.read_csv(raw_path, sep="\t")
    if suffix in {".xls", ".xlsx"}:
        return pd.read_excel(raw_path)
    raise ValueError(f"Unsupported raw retail dataset format: {raw_path.suffix}")


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

        yield {
            "id": stock_code,
            "name": str(reference_row["description"]),
            "observations": observations,
            "price_arms": price_arms,
            "empirical_rewards": [
                {"arm": _round_float(arm), "rewards": rewards}
                for arm, rewards in sorted(price_rewards.items())
            ],
            "elasticity_model": {
                "base_price": _round_float(base_price),
                "base_demand": _round_float(max(1.0, mean_quantity)),
                "elasticity": _round_float(elasticity),
                "noise_scale": 0.05,
            },
        }


def _round_float(value: float) -> float:
    return round(float(value), 3)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build sample payloads for frontend fallback.")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--raw-dir", type=Path, default=_DEFAULT_RAW_DIR)
    parser.add_argument("--allow-download", action="store_true")
    args = parser.parse_args()
    build_sample_payload(args.output, raw_dir=args.raw_dir, allow_download=args.allow_download)


if __name__ == "__main__":
    main()

