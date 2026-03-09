# ETF Relative Strength Dashboard (V1)

Beginner-friendly full-stack project that stores ETF price history, computes ranking metrics, and renders a dashboard.

## Tech stack
- **Backend:** Python + SQLite + built-in HTTP server
- **Frontend:** React + Vite
- **API style:** simple REST API

## Project structure

```text
backend/
  app/
    api/            # REST endpoints
    db/             # SQLite connection + schema setup
    services/       # price fetch, metrics, ranking, summary logic
    main.py         # backend HTTP server entrypoint
  scripts/          # run pipeline tasks in order
frontend/
  src/
    components/     # reusable UI pieces
    pages/          # Dashboard page
data/
  starter_tickers.csv
```

## Database tables
Created by `backend/app/db/database.py`:
- `tickers`
- `price_history` (with unique `ticker_id,date`)
- `computed_metrics`
- `dashboard_summary`

## Required scripts and order
Run from repository root:

1. Seed starter universe:
   ```bash
   python backend/scripts/seed_tickers.py
   ```
2. Fetch daily prices:
   ```bash
   python backend/scripts/fetch_prices.py
   ```
3. Compute metrics + ranking:
   ```bash
   python backend/scripts/compute_metrics.py
   ```
4. Build dashboard summary:
   ```bash
   python backend/scripts/build_summary.py
   ```

## Where formulas are implemented
- Return + moving averages + trend/obos/score formulas: `backend/app/services/metrics_service.py`
- Rank fields + momentum/signal labels: `backend/app/services/ranking_service.py`
- Summary breadth and market health rollups: `backend/app/services/summary_service.py`

## API endpoints
- `GET /api/dashboard/latest`
- `GET /api/metrics/latest`
- `GET /api/prices/sparkline/:symbol`

## Local setup

### 1) Backend
```bash
python -m venv .venv
source .venv/bin/activate
python backend/scripts/seed_tickers.py
python backend/scripts/fetch_prices.py
python backend/scripts/compute_metrics.py
python backend/scripts/build_summary.py
python backend/app/main.py
```
Backend runs at `http://localhost:5000`.

### 2) Frontend
```bash
cd frontend
npm install
cp ../.env.example .env
npm run dev
```
Frontend runs at `http://localhost:5173`.

## Beginner notes
- Services are intentionally split by responsibility so each file is easier to reason about.
- Scripts are plain Python files (no task runners) so you can step through each stage.
- The frontend fetches API data and renders simple table/panel components.
