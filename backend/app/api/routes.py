"""Simple API helpers used by the builtin HTTP server."""
from __future__ import annotations

import json

from app.db.database import get_connection


def get_dashboard_latest() -> tuple[int, dict]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM dashboard_summary ORDER BY date DESC LIMIT 1").fetchone()
    if not row:
        return 404, {"message": "No dashboard summary available"}

    payload = dict(row)
    for key in ["top_5_movers_json", "top_entries_json", "pullback_entries_json", "group_summary_json"]:
        payload[key.replace("_json", "")] = json.loads(payload[key] or "[]")
    return 200, payload


def get_metrics_latest() -> tuple[int, list[dict]]:
    with get_connection() as conn:
        latest = conn.execute("SELECT MAX(date) as d FROM computed_metrics").fetchone()["d"]
        if not latest:
            return 200, []
        rows = conn.execute(
            """
            SELECT t.symbol, t.name, cm.*
            FROM computed_metrics cm
            JOIN tickers t ON t.id = cm.ticker_id
            WHERE cm.date = ?
            ORDER BY cm.rank_today
            """,
            (latest,),
        ).fetchall()
    return 200, [dict(r) for r in rows]


def get_sparkline(symbol: str) -> tuple[int, list[dict]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT p.date, p.close
            FROM price_history p
            JOIN tickers t ON t.id = p.ticker_id
            WHERE t.symbol = ?
            ORDER BY p.date DESC
            LIMIT 30
            """,
            (symbol.upper(),),
        ).fetchall()
    return 200, list(reversed([dict(r) for r in rows]))
