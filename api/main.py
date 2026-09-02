import json
from typing import Any



from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.screener.engine import (
    load_screener_data,
    run_preset,
    run_screener,
)


app = FastAPI(
    title="N100 Financial Intelligence API",
    version="1.0.0",
    description="API for N100 financial screening and intelligence.",
)


# ============================================================
# ROOT / HEALTH
# ============================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "N100 Financial Intelligence API is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# ============================================================
# COMPANIES
# ============================================================

@app.get("/companies")
def companies():
    """Return all N100 companies."""

    df = load_screener_data()

    columns = [
        column
        for column in [
            "company_id",
            "company_name",
            "broad_sector",
            "market_cap_cr",
            "sales",
            "return_on_equity_pct",
            "debt_to_equity",
        ]
        if column in df.columns
    ]

    records = json.loads(
        df[columns].to_json(
            orient="records"
        )
    )

    return {
        "count": len(df),
        "companies": records,
    }

@app.get("/companies/{company_id}")
def company_detail(company_id: str):
    """Return details for one company."""

    df = load_screener_data()

    if "company_id" not in df.columns:
        raise HTTPException(
            status_code=500,
            detail="company_id column not available",
        )

    matches = df[
        df["company_id"]
        .astype(str)
        .str.upper()
        == company_id.upper()
    ]

    if matches.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Company '{company_id}' not found",
        )

    record = json.loads(
        matches.iloc[[0]].to_json(
            orient="records"
        )
    )[0]

    return record


# ============================================================
# PRESETS
# ============================================================

PRESETS = [
    "quality_compounder",
    "value_pick",
    "growth_accelerator",
    "dividend_champion",
    "debt_free_blue_chip",
    "turnaround_watch",
]


@app.get("/presets")
def presets():
    """Return available screener presets."""

    return {
        "count": len(PRESETS),
        "presets": PRESETS,
    }


@app.get("/presets/{preset_name}")
def preset_results(preset_name: str):
    """Run a configured preset."""

    if preset_name not in PRESETS:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Unknown preset '{preset_name}'. "
                f"Available presets: {PRESETS}"
            ),
        )

    print("DEBUG: preset endpoint started", flush=True)

    df = run_preset(preset_name)

    print("DEBUG: after run_preset", len(df), flush=True)

    columns = [
        column
        for column in [
            "company_id",
            "company_name",
            "broad_sector",
            "market_cap_cr",
            "sales",
            "return_on_equity_pct",
            "debt_to_equity",
            "composite_quality_score",
        ]
        if column in df.columns
    ]

    records = json.loads(
        df[columns].to_json(orient="records")
    )

    return {
        "preset": preset_name,
        "count": len(df),
        "results": records,
    }@app.get("/companies/{company_id}/peers")
def company_peer_comparison(company_id: str):
    """Return peer comparison for a company."""

    from src.analytics.peer_comparison import peer_comparison, add_peer_ranks

    df = peer_comparison(company_id)

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No peer comparison found for '{company_id}'",
        )

    ranked = add_peer_ranks(df)

    return {
        "company_id": company_id,
        "peer_group_name": ranked.iloc[0]["peer_group_name"],
        "peer_count": len(ranked),
        "results": json.loads(
            ranked.to_json(orient="records")
        ),
    }
# ============================================================
# CUSTOM SCREENER
# ============================================================

class ScreenerRequest(BaseModel):
    roe_min: float | None = None
    debt_to_equity_max: float | None = None
    fcf_min: float | None = None
    revenue_cagr_5yr_min: float | None = None
    pat_cagr_5yr_min: float | None = None
    opm_min: float | None = None
    pe_max: float | None = None
    pb_max: float | None = None
    dividend_yield_min: float | None = None
    icr_min: float | None = None
    market_cap_min: float | None = None
    net_profit_min: float | None = None
    eps_cagr_5yr_min: float | None = None
    asset_turnover_min: float | None = None
    sales_min: float | None = None
    dividend_payout_max: float | None = None


@app.post("/screener")
def custom_screener(request: ScreenerRequest):
    """Run the custom screener using supplied filters."""

    filters = request.model_dump(
        exclude_none=True
    )

    try:
        df = run_screener(filters)

        columns = [
            column
            for column in [
                "company_id",
                "company_name",
                "broad_sector",
                "market_cap_cr",
                "sales",
                "return_on_equity_pct",
                "return_on_capital_employed_pct",
                "net_profit_margin_pct",
                "free_cash_flow_cr",
                "revenue_cagr_5yr",
                "pat_cagr_5yr",
                "debt_to_equity",
                "interest_coverage",
                "composite_quality_score",
            ]
            if column in df.columns
        ]

        result = df[columns].copy()

        # Convert NaN values to None for valid JSON
        result = result.astype(object)
        result = result.where(result.notna(), None)

        return {
            "filters": filters,
            "count": len(result),
            "results": result.to_dict(
                orient="records"
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Screener error: {type(exc).__name__}: {exc}",
        )


    
@app.get("/companies/{company_id}/peers")
def company_peer_comparison(company_id: str):
    """Return peer comparison for a company."""

    from src.analytics.peer_comparison import peer_comparison, add_peer_ranks

    df = peer_comparison(company_id)

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No peer comparison found for '{company_id}'",
        )

    ranked = add_peer_ranks(df)

    return {
        "company_id": company_id,
        "peer_group_name": ranked.iloc[0]["peer_group_name"],
        "peer_count": len(ranked),
        "results": json.loads(
            ranked.to_json(orient="records")
        ),
    }