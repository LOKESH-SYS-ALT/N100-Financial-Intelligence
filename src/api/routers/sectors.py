import sqlite3
from fastapi import APIRouter, Depends, HTTPException
from src.api.dependencies import get_db

router = APIRouter(
    prefix="/api/v1/sectors",
    tags=["Sectors"],
)


@router.get("")
def list_sectors(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute("""
        SELECT
            broad_sector AS sector,
            COUNT(*) AS company_count
        FROM sectors
        GROUP BY broad_sector
        ORDER BY broad_sector
        """).fetchall()

    return {
        "count": len(rows),
        "sectors": [dict(row) for row in rows],
    }


@router.get("/{sector_name}/companies")
def sector_companies(
    sector_name: str,
    db: sqlite3.Connection = Depends(get_db),
):
    rows = db.execute(
        """
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector AS sector,
            s.sub_sector AS sub_sector
        FROM companies c
        JOIN sectors s
            ON c.id = s.company_id
        WHERE LOWER(s.broad_sector) = LOWER(?)
        ORDER BY c.id
        """,
        (sector_name,),
    ).fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"Sector not found: {sector_name}",
        )

    return {
        "sector": sector_name,
        "count": len(rows),
        "companies": [dict(row) for row in rows],
    }
