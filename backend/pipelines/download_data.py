from __future__ import annotations

from pathlib import Path

import requests


_UCI_FILENAME = "Online Retail.xlsx"
_UCI_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
_LOCAL_PATTERNS = (
    "Online Retail.xlsx",
    "Online Retail.xls",
    "Online Retail.csv",
    "Online Retail.tsv",
    "Online Retail.*",
)


def find_local_uci_online_retail(raw_dir: Path) -> Path | None:
    raw_dir = Path(raw_dir)
    for pattern in _LOCAL_PATTERNS:
        matches = sorted(raw_dir.glob(pattern))
        if matches:
            return matches[0]
    return None


def download_uci_online_retail(raw_dir: Path) -> Path:
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    existing_file = find_local_uci_online_retail(raw_dir)
    if existing_file is not None:
        return existing_file

    destination = raw_dir / _UCI_FILENAME
    try:
        response = requests.get(_UCI_URL, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            "Unable to download the UCI Online Retail dataset. "
            "Generate samples with synthetic fallback instead."
        ) from exc

    destination.write_bytes(response.content)
    return destination
