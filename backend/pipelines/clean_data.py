from __future__ import annotations

import math
import random

import pandas as pd


_COLUMN_RENAMES = {
    "InvoiceNo": "invoice_no",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "UnitPrice": "unit_price",
    "CustomerID": "customer_id",
    "Country": "country",
}

_PRODUCT_SPECS = [
    {"stock_code": "SYN-001", "description": "Ceramic Mug", "base_price": 9.5, "base_demand": 26.0, "elasticity": -1.15},
    {"stock_code": "SYN-002", "description": "Canvas Tote", "base_price": 14.0, "base_demand": 18.0, "elasticity": -1.05},
    {"stock_code": "SYN-003", "description": "Glass Vase", "base_price": 24.0, "base_demand": 10.0, "elasticity": -1.35},
    {"stock_code": "SYN-004", "description": "LED Lantern", "base_price": 29.5, "base_demand": 8.0, "elasticity": -0.95},
    {"stock_code": "SYN-005", "description": "Wool Throw", "base_price": 39.0, "base_demand": 7.0, "elasticity": -0.85},
]


def clean_transactions(frame: pd.DataFrame) -> pd.DataFrame:
    cleaned = frame.rename(columns=_COLUMN_RENAMES).copy()
    cleaned.columns = [str(column).strip().lower() for column in cleaned.columns]

    cleaned["invoice_no"] = cleaned["invoice_no"].astype(str).str.strip()
    cleaned["description"] = cleaned["description"].fillna("").astype(str).str.strip()
    cleaned["quantity"] = pd.to_numeric(cleaned["quantity"], errors="coerce")
    cleaned["unit_price"] = pd.to_numeric(cleaned["unit_price"], errors="coerce")
    cleaned["invoice_date"] = pd.to_datetime(cleaned["invoice_date"], errors="coerce")
    if "country" not in cleaned.columns:
        cleaned["country"] = "United Kingdom"

    filtered = cleaned.loc[
        ~cleaned["invoice_no"].str.startswith("C")
        & (cleaned["quantity"] > 0)
        & (cleaned["unit_price"] > 0)
        & cleaned["invoice_date"].notna()
        & (cleaned["description"] != "")
    ].copy()
    filtered["revenue"] = filtered["quantity"] * filtered["unit_price"]

    return filtered.reset_index(drop=True)


def build_synthetic_transactions(seed: int = 0) -> pd.DataFrame:
    rng = random.Random(seed)
    rows: list[dict[str, object]] = []
    start = pd.Timestamp("2011-01-01")

    for day_index in range(365):
        current_day = start + pd.Timedelta(days=day_index)
        seasonal_multiplier = 1.0 + 0.18 * math.sin((2.0 * math.pi * day_index) / 365.0)

        for product_index, spec in enumerate(_PRODUCT_SPECS):
            price_factor = 0.9 + (0.05 * ((day_index + product_index) % 5))
            unit_price = round(spec["base_price"] * price_factor, 2)
            expected_demand = max(
                1.0,
                spec["base_demand"]
                * (unit_price / spec["base_price"]) ** spec["elasticity"]
                * seasonal_multiplier
                * rng.uniform(0.9, 1.1),
            )
            quantity = max(1, int(round(expected_demand)))
            rows.append(
                {
                    "stock_code": spec["stock_code"],
                    "description": spec["description"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "invoice_date": current_day,
                    "country": "United Kingdom",
                    "revenue": round(quantity * unit_price, 2),
                }
            )

    return pd.DataFrame(rows)


def select_sample_products(frame: pd.DataFrame, count: int = 3) -> pd.DataFrame:
    if count <= 0:
        raise ValueError("count must be positive")

    ranked_codes = (
        frame.groupby("stock_code", as_index=False)["revenue"]
        .sum()
        .sort_values(["revenue", "stock_code"], ascending=[False, True])
        .head(count)["stock_code"]
        .tolist()
    )
    selected = frame.loc[frame["stock_code"].isin(ranked_codes)].copy()
    return selected.sort_values(["stock_code", "invoice_date"]).reset_index(drop=True)
