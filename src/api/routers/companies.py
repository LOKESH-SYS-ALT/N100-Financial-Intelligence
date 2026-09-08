import sqlite3
from fastapi import APIRouter, Depends, HTTPException, Query
from src.api.dependencies import get_db

router = APIRouter(prefix="/api/v1/companies", tags=["Companies"])


@router.get("")
def list_companies(
    search: str | None = Query(default=None),
    sector: str | None = Query(default=None),
    db: sqlite3.Connection = Depends(get_db),
):
    query = """
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector AS sector,
            s.sub_sector AS sub_sector
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE 1 = 1
    """

    params = []

    if search:
        query += """
            AND (
                c.id LIKE ?
                OR c.company_name LIKE ?
            )
        """
        search_value = f"%{search}%"
        params.extend([search_value, search_value])

    if sector:
        query += " AND s.broad_sector = ? "
        params.append(sector)

    query += " ORDER BY c.id"

    rows = db.execute(query, params).fetchall()

    return {
        "count": len(rows),
        "companies": [dict(row) for row in rows],
    }


@router.get("/{company_id}/documents")
def get_company_documents(
    company_id: str,
    db: sqlite3.Connection = Depends(get_db),
):
    company_id = company_id.upper()

    company = db.execute(
        """
        SELECT id, company_name
        FROM companies
        WHERE id = ?
        """,
        (company_id,),
    ).fetchone()

    if company is None:
        raise HTTPException(
            status_code=404,
            detail=f"Company not found: {company_id}",
        )

    rows = db.execute(
        """
        SELECT *
        FROM documents
        WHERE company_id = ?
        ORDER BY id
        """,
        (company_id,),
    ).fetchall()

    return {
        "company_id": company_id,
        "company_name": company["company_name"],
        "count": len(rows),
        "documents": [dict(row) for row in rows],
    }


@router.get("/{company_id}")
def get_company(
    company_id: str,
    db: sqlite3.Connection = Depends(get_db),
):
    company_id = company_id.upper()

    row = db.execute(
        """
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector AS sector,
            s.sub_sector AS sub_sector,
            s.index_weight_pct,
            s.market_cap_category
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE c.id = ?
        """,
        (company_id,),
    ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Company not found: {company_id}",
        )

    return dict(row)
