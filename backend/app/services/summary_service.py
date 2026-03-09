"""Build one-row dashboard summary from latest computed metrics."""
from __future__ import annotations

import json

from app.db.database import get_connection


def _health_label(avg_trend: float) -> str:
    if avg_trend >= 2.2:
        return "Strong"
    if avg_trend >= 1.4:
        return "Mixed"
    return "Weak"


def build_latest_summary() -> dict:
    with get_connection() as conn:
        latest = conn.execute("SELECT MAX(date) as d FROM computed_metrics").fetchone()["d"]
        if not latest:
            return {"message": "No metrics found"}

        rows = conn.execute(
            """
            SELECT cm.*, t.symbol, t.group_name
            FROM computed_metrics cm
            JOIN tickers t ON t.id = cm.ticker_id
            WHERE cm.date = ?
            ORDER BY cm.rank_today
            """,
            (latest,),
        ).fetchall()

    total = len(rows) or 1
    pct_above_10dma = sum(r["above_10dma"] for r in rows) / total * 100
    pct_above_20dma = sum(r["above_20dma"] for r in rows) / total * 100
    pct_above_50dma = sum(r["above_50dma"] for r in rows) / total * 100
    avg_trend = sum(r["trend_score"] for r in rows) / total

    top_5_movers = [
        {"symbol": r["symbol"], "rank_change_5d": r["rank_change_5d"]}
        for r in sorted(rows, key=lambda x: x["rank_change_5d"] or -999, reverse=True)[:5]
    ]
    top_entries = [
        {"symbol": r["symbol"], "rank": r["rank_today"], "signal": r["signal_label"]}
        for r in rows[:10]
        if r["signal_label"] in ("Continuation", "Pullback")
    ]
    pullback_entries = [
        {"symbol": r["symbol"], "obos_score": r["obos_score"], "label": r["pullback_depth_label"]}
        for r in rows
        if r["signal_label"] == "Pullback"
    ]

    group_buckets = {}
    for r in rows:
        bucket = group_buckets.setdefault(r["group_name"], {"count": 0, "avg_rs": 0.0})
        bucket["count"] += 1
        bucket["avg_rs"] += r["rs_score"] or 0.0
    group_summary = {
        g: {"count": b["count"], "avg_rs": (b["avg_rs"] / b["count"]) if b["count"] else 0}
        for g, b in group_buckets.items()
    }

    payload = {
        "date": latest,
        "pct_above_10dma": pct_above_10dma,
        "pct_above_20dma": pct_above_20dma,
        "pct_above_50dma": pct_above_50dma,
        "average_trend_score": avg_trend,
        "market_health_label": _health_label(avg_trend),
        "top_5_movers_json": json.dumps(top_5_movers),
        "top_entries_json": json.dumps(top_entries),
        "pullback_entries_json": json.dumps(pullback_entries),
        "group_summary_json": json.dumps(group_summary),
    }

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO dashboard_summary (
                date, pct_above_10dma, pct_above_20dma, pct_above_50dma,
                average_trend_score, market_health_label, top_5_movers_json,
                top_entries_json, pullback_entries_json, group_summary_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                pct_above_10dma=excluded.pct_above_10dma,
                pct_above_20dma=excluded.pct_above_20dma,
                pct_above_50dma=excluded.pct_above_50dma,
                average_trend_score=excluded.average_trend_score,
                market_health_label=excluded.market_health_label,
                top_5_movers_json=excluded.top_5_movers_json,
                top_entries_json=excluded.top_entries_json,
                pullback_entries_json=excluded.pullback_entries_json,
                group_summary_json=excluded.group_summary_json
            """,
            (
                payload["date"],
                payload["pct_above_10dma"],
                payload["pct_above_20dma"],
                payload["pct_above_50dma"],
                payload["average_trend_score"],
                payload["market_health_label"],
                payload["top_5_movers_json"],
                payload["top_entries_json"],
                payload["pullback_entries_json"],
                payload["group_summary_json"],
            ),
        )

    return payload
