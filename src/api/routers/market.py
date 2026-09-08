from pathlib import Path
import sqlite3
import pandas as pd

from fastapi import APIRouter, Depends
from src.api.dependencies import get_db

router = APIRouter(prefix="/api/v1/market", tags=["Market"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PORTFOLIO_STATS_PATH = PROJECT_ROOT / "output" / "portfolio_stats.csv"


@router.get("/market-cap")
def market_cap(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute("SELECT * FROM market_cap ORDER BY company_id, year").fetchall()

    return {
        "count": len(rows),
        "market_cap": [dict(row) for row in rows],
    }


@router.get("/portfolio-stats")
def portfolio_stats():
    if not PORTFOLIO_STATS_PATH.exists():
        return {
            "count": 0,
            "portfolio_stats": [],
            "error": f"Portfolio stats file not found: {PORTFOLIO_STATS_PATH}",
        }

    df = pd.read_csv(PORTFOLIO_STATS_PATH)

    return {
        "count": len(df),
        "portfolio_stats": df.where(pd.notna(df), None).to_dict(orient="records"),
    }
