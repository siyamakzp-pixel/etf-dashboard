"""Load starter ETF universe from CSV into tickers table."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "backend"))

from app.db.database import get_connection, init_db


def main() -> None:
    init_db()
    csv_path = ROOT / "data" / "starter_tickers.csv"
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                row["symbol"].upper(),
                row["name"],
                row["group_name"],
                row["subgroup_name"],
                int(row["sort_order"]),
                int(row["is_active"]),
            )
            for row in reader
        ]

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO tickers (symbol, name, group_name, subgroup_name, sort_order, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                name=excluded.name,
                group_name=excluded.group_name,
                subgroup_name=excluded.subgroup_name,
                sort_order=excluded.sort_order,
                is_active=excluded.is_active
            """,
            rows,
        )
    print(f"Seeded {len(rows)} tickers")


if __name__ == "__main__":
    main()
