from pathlib import Path
import logging
import sqlite3
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import health as health_router
from src.api.routers import companies as companies_router
from src.api.routers import financials as financials_router
from src.api.routers import screener as screener_router
from src.api.routers import sectors as sectors_router
from src.api.routers import peers as peers_router
from src.api.routers import market as market_router
from src.api.routers import reports as reports_router

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"

VERSION = "1.0.0"

START_TIME = time.time()


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("n100-api")


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="N100 Financial Intelligence API",
    description=(
        "REST API for N100 Financial Intelligence Platform. "
        "Provides company financials, screening, peer analysis, "
        "sector intelligence, market data and reports."
    ),
    version=VERSION,
)

app.include_router(health_router.router)
app.include_router(companies_router.router)
app.include_router(financials_router.router)
app.include_router(screener_router.router)
app.include_router(sectors_router.router)
app.include_router(peers_router.router)
app.include_router(market_router.router)
app.include_router(reports_router.router)
# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE
# ============================================================


def get_db_connection():
    """Return SQLite database connection."""

    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    return sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
    )


def get_db_row_counts():
    """Return row counts for all database tables."""

    conn = get_db_connection()

    try:
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

        counts = {}

        for table in tables:

            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

                counts[table] = count

            except sqlite3.Error:

                counts[table] = None

        return counts

    finally:
        conn.close()


# ============================================================
# ROOT
# ============================================================


@app.get(
    "/",
    tags=["System"],
)
def root():
    """API welcome endpoint."""

    return {
        "name": "N100 Financial Intelligence API",
        "version": VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


# ============================================================
# STARTUP / SHUTDOWN
# ============================================================


@app.on_event("startup")
async def startup_event():
    """Log API startup."""

    logger.info("N100 Financial Intelligence API started")

    logger.info(
        "Database: %s",
        DB_PATH,
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Log API shutdown."""

    logger.info("N100 Financial Intelligence API stopped")
