from pathlib import Path
import sqlite3

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from src.api.dependencies import get_db

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEARSHEET_DIR = PROJECT_ROOT / "reports" / "tearsheets"


@router.get("/status")
def reports_status():
    return {"status": "ok", "message": "Reports router is running"}


@router.get("/companies/{company_id}/tearsheet")
def get_tearsheet(
    company_id: str,
    db: sqlite3.Connection = Depends(get_db),
):
    company_id = company_id.upper()

    company = db.execute(
        "SELECT id FROM companies WHERE id = ?",
        (company_id,),
    ).fetchone()

    if company is None:
        raise HTTPException(
            status_code=404,
            detail=f"Company not found: {company_id}",
        )

    pdf_path = TEARSHEET_DIR / f"{company_id}_tearsheet.pdf"

    if not pdf_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Tearsheet not found for company: {company_id}",
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
    )
