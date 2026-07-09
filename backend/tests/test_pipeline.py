from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

import pandas as pd

from pipelines.clean_data import (
    build_synthetic_transactions,
    clean_transactions,
    select_sample_products,
)
from pipelines.make_sample import build_sample_payload


def test_clean_transactions_removes_returns_and_bad_prices():
    raw = pd.DataFrame(
        [
            {
                "InvoiceNo": "1",
                "StockCode": "A",
                "Description": "MUG",
                "Quantity": 2,
                "InvoiceDate": "2011-01-01",
                "UnitPrice": 3.0,
                "CustomerID": 1,
                "Country": "UK",
            },
            {
                "InvoiceNo": "C2",
                "StockCode": "A",
                "Description": "MUG",
                "Quantity": -1,
                "InvoiceDate": "2011-01-02",
                "UnitPrice": 3.0,
                "CustomerID": 1,
                "Country": "UK",
            },
            {
                "InvoiceNo": "3",
                "StockCode": "B",
                "Description": "BAG",
                "Quantity": 1,
                "InvoiceDate": "2011-01-03",
                "UnitPrice": 0.0,
                "CustomerID": 2,
                "Country": "UK",
            },
        ]
    )

    cleaned = clean_transactions(raw)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["revenue"] == 6.0


def test_synthetic_transactions_have_required_columns():
    frame = build_synthetic_transactions(seed=4)

    assert {
        "stock_code",
        "description",
        "quantity",
        "unit_price",
        "invoice_date",
        "revenue",
    }.issubset(frame.columns)
    assert len(frame) >= 100


def test_select_sample_products_returns_requested_count():
    frame = build_synthetic_transactions(seed=4)

    selected = select_sample_products(frame, count=3)

    assert len(selected["stock_code"].unique()) == 3


def test_build_sample_payload_writes_small_network_free_samples():
    output_dir = Path("tests") / "_tmp" / f"sample-payload-{uuid.uuid4().hex}"

    try:
        build_sample_payload(output_dir)

        catalog_path = output_dir / "catalog.json"
        results_path = output_dir / "precomputed_results.json"

        assert catalog_path.exists()
        assert results_path.exists()
        assert catalog_path.stat().st_size < 20_000
        assert results_path.stat().st_size < 200_000

        catalog = json.loads(catalog_path.read_text())
        results = json.loads(results_path.read_text())

        assert catalog["source"] == "UCI Online Retail or synthetic fallback"
        assert catalog["products"]
        assert results["products"]
        assert {"empirical", "elasticity"} <= set(results["products"][0]["environments"])
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)
