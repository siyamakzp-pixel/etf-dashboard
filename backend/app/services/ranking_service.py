"""Ranking logic: assigns cross-sectional RS ranks and labels."""
from __future__ import annotations

from collections import defaultdict

from app.db.database import get_connection


def _momentum_label(change: int | None) -> str:
    if change is None:
        return "Neutral"
    if change >= 10:
        return "Very Strong"
    if 5 <= change <= 9:
        return "Strong Climb"
    if -4 <= change <= 4:
        return "Neutral"
    if change <= -5:
        return "Weakening"
    return "Neutral"


def _signal_label(row: dict) -> str:
    rank_today = row["rank_today"]
    weekly_return = row["weekly_return"]
    monthly_return = row["monthly_return"]
    trend_score = row["trend_score"]
    obos_score = row["obos_score"]
    daily_return = row["daily_return"]

    if None in (rank_today, weekly_return, monthly_return, trend_score, obos_score):
        return "Neutral"

    if (
        rank_today <= 5
        and weekly_return > 0
        and monthly_return > 0
        and trend_score >= 2
        and 0 <= obos_score <= 4
    ):
        return "Continuation"

    if (
        rank_today <= 15
        and monthly_return > 0
        and trend_score >= 2
        and (daily_return or 0) < 0
        and -4 <= obos_score <= 0
    ):
        return "Pullback"

    if monthly_return < 0 and obos_score < -4 and rank_today > 20:
        return "Mean Reversion Watch"

    return "Neutral"


def apply_rankings() -> int:
    """Rank ETFs by date and calculate momentum/rank-change fields."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, ticker_id, date, rs_score, daily_return, weekly_return,
                   monthly_return, trend_score, obos_score
            FROM computed_metrics
            ORDER BY date, rs_score DESC
            """
        ).fetchall()

    by_date = defaultdict(list)
    for row in rows:
        by_date[row["date"]].append(dict(row))

    sorted_dates = sorted(by_date)
    rank_cache: dict[str, dict[int, int]] = {}

    for d in sorted_dates:
        ranked = sorted(
            by_date[d], key=lambda r: (r["rs_score"] is None, -(r["rs_score"] or -999999))
        )
        rank_cache[d] = {row["ticker_id"]: idx + 1 for idx, row in enumerate(ranked)}

    updates = []
    for idx, d in enumerate(sorted_dates):
        for row in by_date[d]:
            ticker_id = row["ticker_id"]
            rank_today = rank_cache[d].get(ticker_id)

            rank_5d_ago = rank_cache[sorted_dates[idx - 5]].get(ticker_id) if idx >= 5 else None
            rank_t_minus_2 = rank_cache[sorted_dates[idx - 2]].get(ticker_id) if idx >= 2 else None
            rank_t_minus_1 = rank_cache[sorted_dates[idx - 1]].get(ticker_id) if idx >= 1 else None

            rank_change_5d = (rank_5d_ago - rank_today) if rank_5d_ago and rank_today else None
            momentum_change_3d = (rank_t_minus_2 - rank_today) if rank_t_minus_2 and rank_today else None
            momentum_label = _momentum_label(momentum_change_3d)

            signal_label = _signal_label(
                {
                    **row,
                    "rank_today": rank_today,
                }
            )

            updates.append(
                (
                    rank_today,
                    rank_5d_ago,
                    rank_change_5d,
                    rank_t_minus_2,
                    rank_t_minus_1,
                    momentum_change_3d,
                    momentum_label,
                    signal_label,
                    row["id"],
                )
            )

    with get_connection() as conn:
        conn.executemany(
            """
            UPDATE computed_metrics
            SET rank_today=?, rank_5d_ago=?, rank_change_5d=?,
                rank_t_minus_2=?, rank_t_minus_1=?, momentum_change_3d=?,
                momentum_label=?, signal_label=?
            WHERE id=?
            """,
            updates,
        )
    return len(updates)
