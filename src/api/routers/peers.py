import sqlite3
from fastapi import APIRouter, Depends, HTTPException, Query
from src.api.dependencies import get_db

router = APIRouter(
    prefix="/api/v1/peers",
    tags=["Peers"],
)


@router.get("")
def list_peer_groups(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute("""
        SELECT *
        FROM peer_groups
        ORDER BY company_id
        """).fetchall()

    return {
        "count": len(rows),
        "peer_groups": [dict(row) for row in rows],
    }


@router.get("/compare")
def compare_peers(
    company_id: str = Query(...),
    db: sqlite3.Connection = Depends(get_db),
):
    company_id = company_id.upper()

    group = db.execute(
        """
        SELECT peer_group_name
        FROM peer_groups
        WHERE company_id = ?
        LIMIT 1
        """,
        (company_id,),
    ).fetchone()

    if not group:
        raise HTTPException(
            status_code=404,
            detail=f"Peer group not found for company: {company_id}",
        )

    rows = db.execute(
        """
        SELECT *
        FROM peer_groups
        WHERE peer_group_name = ?
        ORDER BY company_id
        """,
        (group["peer_group_name"],),
    ).fetchall()

    return {
        "company_id": company_id,
        "peer_group_name": group["peer_group_name"],
        "count": len(rows),
        "peers": [dict(row) for row in rows],
    }


@router.get("/{company_id}")
def get_company_peers(
    company_id: str,
    db: sqlite3.Connection = Depends(get_db),
):
    company_id = company_id.upper()

    rows = db.execute(
        """
        SELECT *
        FROM peer_groups
        WHERE company_id = ?
        """,
        (company_id,),
    ).fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"Peer group not found for company: {company_id}",
        )

    return {
        "company_id": company_id,
        "count": len(rows),
        "peers": [dict(row) for row in rows],
    }
