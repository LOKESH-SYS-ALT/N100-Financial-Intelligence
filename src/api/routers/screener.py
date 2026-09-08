import sqlite3
from fastapi import APIRouter, Depends, Query
from src.api.dependencies import get_db

router = APIRouter(
    prefix="/api/v1/screener",
    tags=["Screener"],
)


@router.get("")
def screen_companies(
    min_roe: float | None = Query(default=None),
    max_de: float | None = Query(default=None),
    min_revenue_cagr: float | None = Query(default=None),
    db: sqlite3.Connection = Depends(get_db),
):
    query = """
        SELECT
            fr.company_id,
            fr.year,
            fr.return_on_equity_pct AS roe,
            fr.debt_to_equity,
            fr.revenue_cagr_5yr
        FROM financial_ratios fr
        WHERE fr.year != 'TTM'
          AND fr.year = (
              SELECT fr2.year
              FROM financial_ratios fr2
              WHERE fr2.company_id = fr.company_id
                AND fr2.year != 'TTM'
              ORDER BY
                  CAST(substr(fr2.year, -4) AS INTEGER) DESC,
                  CASE
                      WHEN fr2.year LIKE 'Mar %' THEN 1
                      WHEN fr2.year LIKE 'Dec %' THEN 2
                      WHEN fr2.year LIKE 'Jun %' THEN 3
                      WHEN fr2.year LIKE 'Sep %' THEN 4
                      ELSE 5
                  END
              LIMIT 1
          )
    """

    conditions = []
    params = []

    if min_roe is not None:
        conditions.append("fr.return_on_equity_pct >= ?")
        params.append(min_roe)

    if max_de is not None:
        conditions.append("fr.debt_to_equity <= ?")
        params.append(max_de)

    if min_revenue_cagr is not None:
        conditions.append("fr.revenue_cagr_5yr >= ?")
        params.append(min_revenue_cagr)

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " ORDER BY fr.company_id"

    rows = db.execute(query, params).fetchall()

    return {
        "count": len(rows),
        "results": [dict(row) for row in rows],
    }
