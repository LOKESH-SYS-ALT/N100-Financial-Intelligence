import sqlite3
import time

from fastapi import APIRouter, Depends

from src.api.dependencies import get_db

router = APIRouter(
    prefix="/api/v1",
    tags=["System"],
)

START_TIME = time.time()


@router.get("/health")
def health(db: sqlite3.Connection = Depends(get_db)):
    """
    Check API and database health.
    """

    tables = [
        "companies",
        "profitandloss",
        "balancesheet",
        "cashflow",
        "analysis",
        "documents",
        "prosandcons",
        "financial_ratios",
        "market_cap",
        "peer_groups",
        "sectors",
        "stock_prices",
    ]

    row_counts = {}

    for table in tables:
        row_counts[table] = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    return {
        "status": "ok",
        "database": "ok",
        "db_row_counts": row_counts,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "version": "1.0.0",
    }
