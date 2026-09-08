from pathlib import Path
import sqlite3

from fastapi import HTTPException

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"


def get_db():
    """
    Provide a SQLite database connection for API endpoints.
    """
    if not DB_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Database not found: {DB_PATH}",
        )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
    finally:
        conn.close()
