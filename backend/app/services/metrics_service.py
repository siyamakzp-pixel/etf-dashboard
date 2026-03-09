"""Compute indicator and return metrics from raw daily prices."""
from __future__ import annotations

from collections import defaultdict

from app.db.database import get_connection


def _avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _label_pullback(obos_score: float | None) -> str:
    if obos_score is None:
        return "Neutral"
    if -2 <= obos_score <= 0:
        return "Shallow Pullback"
    if -4 <= obos_score < -2:
        return "Moderate Pullback"
    if obos_score < -4:
        return "Deep Pullback"
    return "Neutral"


def _safe_return(today: float, prior: float | None) -> float | None:
    if prior in (None, 0):
        return None
    return (today / prior) - 1


def compute_metrics() -> int:
    """Compute metrics row-by-row for every ticker and trade date."""
    with get_connection() as conn:
        prices = conn.execute(
            """
            SELECT p.ticker_id, p.date, p.close
            FROM price_history p
            JOIN tickers t ON t.id = p.ticker_id
            WHERE t.is_active = 1
            ORDER BY p.ticker_id, p.date
            """
        ).fetchall()

    by_ticker: dict[int, list] = defaultdict(list)
    for row in prices:
        by_ticker[row["ticker_id"]].append(row)

    inserts: list[tuple] = []
    for ticker_id, rows in by_ticker.items():
        closes = [r["close"] for r in rows]
        for i, row in enumerate(rows):
            close_today = closes[i]
            ma10 = _avg(closes[max(0, i - 9) : i + 1]) if i >= 9 else None
            ma20 = _avg(closes[max(0, i - 19) : i + 1]) if i >= 19 else None
            ma50 = _avg(closes[max(0, i - 49) : i + 1]) if i >= 49 else None

            daily_return = _safe_return(close_today, closes[i - 1] if i >= 1 else None)
            weekly_return = _safe_return(close_today, closes[i - 5] if i >= 5 else None)
            monthly_return = _safe_return(close_today, closes[i - 21] if i >= 21 else None)

            above_10dma = int(ma10 is not None and close_today > ma10)
            above_20dma = int(ma20 is not None and close_today > ma20)
            above_50dma = int(ma50 is not None and close_today > ma50)
            trend_score = above_10dma + above_20dma + above_50dma
            obos_score = ((close_today / ma10) - 1) * 100 if ma10 else None

            short_term_score = None
            long_term_score = None
            rs_score = None
            if None not in (daily_return, weekly_return, monthly_return):
                short_term_score = 0.50 * weekly_return + 0.30 * daily_return + 0.20 * monthly_return
                long_term_score = 0.70 * monthly_return + 0.30 * weekly_return
                rs_score = 0.60 * short_term_score + 0.40 * long_term_score

            inserts.append(
                (
                    ticker_id,
                    row["date"],
                    daily_return,
                    weekly_return,
                    monthly_return,
                    ma10,
                    ma20,
                    ma50,
                    above_10dma,
                    above_20dma,
                    above_50dma,
                    trend_score,
                    obos_score,
                    short_term_score,
                    long_term_score,
                    rs_score,
                    _label_pullback(obos_score),
                )
            )

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO computed_metrics (
                ticker_id, date, daily_return, weekly_return, monthly_return,
                ma10, ma20, ma50, above_10dma, above_20dma, above_50dma,
                trend_score, obos_score, short_term_score, long_term_score, rs_score,
                pullback_depth_label
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker_id, date) DO UPDATE SET
                daily_return=excluded.daily_return,
                weekly_return=excluded.weekly_return,
                monthly_return=excluded.monthly_return,
                ma10=excluded.ma10,
                ma20=excluded.ma20,
                ma50=excluded.ma50,
                above_10dma=excluded.above_10dma,
                above_20dma=excluded.above_20dma,
                above_50dma=excluded.above_50dma,
                trend_score=excluded.trend_score,
                obos_score=excluded.obos_score,
                short_term_score=excluded.short_term_score,
                long_term_score=excluded.long_term_score,
                rs_score=excluded.rs_score,
                pullback_depth_label=excluded.pullback_depth_label
            """,
            inserts,
        )
    return len(inserts)
