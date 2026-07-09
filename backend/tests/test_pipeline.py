from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

import pandas as pd

import pipelines.download_data as download_data
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


def test_download_uci_online_retail_prefers_existing_local_file(monkeypatch):
    raw_dir = Path("tests") / "_tmp" / f"download-local-{uuid.uuid4().hex}"
    existing_file = raw_dir / "Online Retail.csv"

    try:
        raw_dir.mkdir(parents=True, exist_ok=True)
        existing_file.write_text("InvoiceNo,StockCode\n1,A\n", encoding="utf-8")

        def fail_if_called(*args, **kwargs):
            raise AssertionError("network should not be used when local raw file exists")

        monkeypatch.setattr(download_data.requests, "get", fail_if_called)

        resolved = download_data.download_uci_online_retail(raw_dir)

        assert resolved == existing_file
    finally:
        shutil.rmtree(raw_dir, ignore_errors=True)


def test_build_sample_payload_uses_local_raw_data_when_provided():
    scratch_root = Path("tests") / "_tmp"
    raw_dir = scratch_root / f"sample-local-raw-{uuid.uuid4().hex}"
    output_dir = scratch_root / f"sample-local-output-{uuid.uuid4().hex}"

    raw_frame = pd.DataFrame(
        [
            {
                "InvoiceNo": "10001",
                "StockCode": "R-001",
                "Description": "Real Mug",
                "Quantity": 3,
                "InvoiceDate": "2011-01-01",
                "UnitPrice": 4.5,
                "CustomerID": 10,
                "Country": "United Kingdom",
            },
            {
                "InvoiceNo": "10002",
                "StockCode": "R-001",
                "Description": "Real Mug",
                "Quantity": 2,
                "InvoiceDate": "2011-01-02",
                "UnitPrice": 5.0,
                "CustomerID": 11,
                "Country": "United Kingdom",
            },
            {
                "InvoiceNo": "10003",
                "StockCode": "R-002",
                "Description": "Real Bowl",
                "Quantity": 1,
                "InvoiceDate": "2011-01-03",
                "UnitPrice": 8.0,
                "CustomerID": 12,
                "Country": "United Kingdom",
            },
        ]
    )

    try:
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_frame.to_csv(raw_dir / "Online Retail.csv", index=False)

        build_sample_payload(output_dir, raw_dir=raw_dir)

        catalog = json.loads((output_dir / "catalog.json").read_text(encoding="utf-8"))
        results = json.loads((output_dir / "precomputed_results.json").read_text(encoding="utf-8"))

        assert catalog["source"] == "uci_online_retail_local"
        assert catalog["products"][0]["id"] == "R-001"
        assert catalog["products"][0]["empirical_rewards"]
        assert catalog["products"][0]["elasticity_model"]["base_price"] > 0
        assert results["products"][0]["id"] == "R-001"
        assert results["products"][0]["name"] == "Real Mug"
    finally:
        shutil.rmtree(raw_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


def test_build_sample_payload_falls_back_to_synthetic_when_download_fails(monkeypatch):
    output_dir = Path("tests") / "_tmp" / f"sample-payload-{uuid.uuid4().hex}"
    raw_dir = Path("tests") / "_tmp" / f"sample-fallback-raw-{uuid.uuid4().hex}"

    try:
        def fail_download(path):
            raise RuntimeError(f"download failed for {path}")

        monkeypatch.setattr("pipelines.make_sample.download_uci_online_retail", fail_download)

        build_sample_payload(output_dir, raw_dir=raw_dir, allow_download=True)

        catalog_path = output_dir / "catalog.json"
        results_path = output_dir / "precomputed_results.json"

        assert catalog_path.exists()
        assert results_path.exists()
        assert catalog_path.stat().st_size < 20_000
        assert results_path.stat().st_size < 200_000

        catalog = json.loads(catalog_path.read_text())
        results = json.loads(results_path.read_text())

        assert catalog["source"] == "synthetic_fallback"
        assert catalog["products"]
        assert catalog["products"][0]["empirical_rewards"]
        assert catalog["products"][0]["elasticity_model"]["noise_scale"] == 0.05
        assert results["products"]
        assert results["products"][0]["id"].startswith("SYN-")
        assert {"empirical", "elasticity"} <= set(results["products"][0]["environments"])
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)
        shutil.rmtree(raw_dir, ignore_errors=True)

