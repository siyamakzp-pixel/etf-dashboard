"""Build latest dashboard_summary row from latest metrics."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "backend"))

from app.db.database import init_db
from app.services.summary_service import build_latest_summary


def main() -> None:
    init_db()
    result = build_latest_summary()
    print(result)


if __name__ == "__main__":
    main()
