"""Compute all numeric metrics and ranking fields."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "backend"))

from app.db.database import init_db
from app.services.metrics_service import compute_metrics
from app.services.ranking_service import apply_rankings


def main() -> None:
    init_db()
    metric_rows = compute_metrics()
    ranked_rows = apply_rankings()
    print({"metrics_rows": metric_rows, "ranked_rows": ranked_rows})


if __name__ == "__main__":
    main()
