import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_db

router = APIRouter(
    prefix="/api/v1/companies",
    tags=["Financials"],
)


def get_company_or_404(
    company_id: str,
    db: sqlite3.Connection,
):
    company_id = company_id.upper()

    row = db.execute(
        """
        SELECT
            id AS company_id,
            company_name
        FROM companies
        WHERE id = ?
        """,
        (company_id,),
    ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Company not found: {company_id}",
        )

    return row


@router.get("/{company_id}/financials/pl")
def get_profit_and_loss(
    company_id: str,
    db: sqlite3.Connection = Depends(get_db),
):
    get_company_or_404(company_id, db)

    rows = db.execute(
        """
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
        ORDER BY year
        """,
        (company_id.upper(),),
    ).fetchall()

    return {
        "company_id": company_id.upper(),
        "count": len(rows),
        "profit_and_loss": [dict(row) for row in rows],
    }


@router.get("/{company_id}/financials/bs")
def get_balance_sheet(
    company_id: str,
    db: sqlite3.Connection = Depends(get_db),
):
    get_company_or_404(company_id, db)

    rows = db.execute(
        """
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
        ORDER BY year
        """,
        (company_id.upper(),),
    ).fetchall()

    return {
        "company_id": company_id.upper(),
        "count": len(rows),
        "balance_sheet": [dict(row) for row in rows],
    }


@router.get("/{company_id}/financials/cashflow")
def get_cash_flow(
    company_id: str,
    db: sqlite3.Connection = Depends(get_db),
):
    get_company_or_404(company_id, db)

    rows = db.execute(
        """
        SELECT *
        FROM cashflow
        WHERE company_id = ?
        ORDER BY year
        """,
        (company_id.upper(),),
    ).fetchall()

    return {
        "company_id": company_id.upper(),
        "count": len(rows),
        "cash_flow": [dict(row) for row in rows],
    }


@router.get("/{company_id}/financials/ratios")
def get_financial_ratios(
    company_id: str,
    db: sqlite3.Connection = Depends(get_db),
):
    get_company_or_404(company_id, db)

    rows = db.execute(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year
        """,
        (company_id.upper(),),
    ).fetchall()

    return {
        "company_id": company_id.upper(),
        "count": len(rows),
        "financial_ratios": [dict(row) for row in rows],
    }
