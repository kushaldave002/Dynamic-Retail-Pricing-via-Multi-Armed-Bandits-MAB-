from __future__ import annotations

from pathlib import Path

import requests


_UCI_FILENAME = "Online Retail.xlsx"
_UCI_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"


def download_uci_online_retail(raw_dir: Path) -> Path:
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    existing_files = sorted(raw_dir.glob("Online Retail.*"))
    if existing_files:
        return existing_files[0]

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
