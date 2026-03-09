"""Fetch and store daily prices for all active tickers."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "backend"))

from app.db.database import init_db
from app.services.price_service import fetch_and_store_all


def main() -> None:
    init_db()
    result = fetch_and_store_all()
    print(result)


if __name__ == "__main__":
    main()
