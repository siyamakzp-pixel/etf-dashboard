"""Database helpers for SQLite connections and schema management."""
from __future__ import annotations

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "backend" / "etf_dashboard.db"


def get_connection() -> sqlite3.Connection:
    """Create a sqlite3 connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create all required tables if they don't exist yet."""
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS tickers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                group_name TEXT NOT NULL,
                subgroup_name TEXT NOT NULL,
                sort_order INTEGER NOT NULL DEFAULT 0,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker_id, date),
                FOREIGN KEY (ticker_id) REFERENCES tickers(id)
            );

            CREATE TABLE IF NOT EXISTS computed_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                daily_return REAL,
                weekly_return REAL,
                monthly_return REAL,
                ma10 REAL,
                ma20 REAL,
                ma50 REAL,
                above_10dma INTEGER,
                above_20dma INTEGER,
                above_50dma INTEGER,
                trend_score INTEGER,
                obos_score REAL,
                short_term_score REAL,
                long_term_score REAL,
                rs_score REAL,
                rank_today INTEGER,
                rank_5d_ago INTEGER,
                rank_change_5d INTEGER,
                rank_t_minus_2 INTEGER,
                rank_t_minus_1 INTEGER,
                momentum_change_3d INTEGER,
                momentum_label TEXT,
                signal_label TEXT,
                pullback_depth_label TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker_id, date),
                FOREIGN KEY (ticker_id) REFERENCES tickers(id)
            );

            CREATE TABLE IF NOT EXISTS dashboard_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                pct_above_10dma REAL,
                pct_above_20dma REAL,
                pct_above_50dma REAL,
                average_trend_score REAL,
                market_health_label TEXT,
                top_5_movers_json TEXT,
                top_entries_json TEXT,
                pullback_entries_json TEXT,
                group_summary_json TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
