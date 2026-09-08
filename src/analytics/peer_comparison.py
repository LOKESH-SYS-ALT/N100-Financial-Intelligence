"""
N100 Financial Intelligence
Peer Comparison Engine

Compares a company against its assigned peer group
using the latest available financial-ratio data.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd

# ============================================================
# CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"


# Metrics where HIGHER is generally better.
HIGHER_IS_BETTER = {
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "interest_coverage",
    "asset_turnover",
    "free_cash_flow_cr",
    "earnings_per_share",
    "book_value_per_share",
    "composite_quality_score",
}

# Metrics where LOWER is generally better.
LOWER_IS_BETTER = {
    "debt_to_equity",
}


# ============================================================
# DATABASE HELPERS
# ============================================================


def get_connection() -> sqlite3.Connection:
    """Return a connection to the project SQLite database."""
    return sqlite3.connect(DB_PATH)


def get_peer_group(company_id: str) -> Optional[str]:
    """
    Return the peer-group name for a company.

    Returns None when the company is not assigned to a peer group.
    """
    query = """
        SELECT peer_group_name
        FROM peer_groups
        WHERE company_id = ?
        LIMIT 1
    """

    with get_connection() as connection:
        row = connection.execute(query, (company_id,)).fetchone()

    if row is None:
        return None

    return row[0]


def get_peer_companies(peer_group_name: str) -> pd.DataFrame:
    """Return all companies belonging to a peer group."""
    query = """
        SELECT
            peer_group_name,
            company_id,
            is_benchmark
        FROM peer_groups
        WHERE peer_group_name = ?
        ORDER BY is_benchmark DESC, company_id
    """

    with get_connection() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=(peer_group_name,),
        )


# ============================================================
# FINANCIAL DATA
# ============================================================


def get_latest_financial_ratios(
    company_ids: list[str],
) -> pd.DataFrame:
    """
    Return the latest financial-ratio record for each company.
    """
    if not company_ids:
        return pd.DataFrame()

    placeholders = ",".join("?" for _ in company_ids)

    query = f"""
        SELECT fr.*
        FROM financial_ratios fr
        INNER JOIN (
            SELECT
                company_id,
                MAX(year) AS latest_year
            FROM financial_ratios
            WHERE company_id IN ({placeholders})
            GROUP BY company_id
        ) latest
            ON fr.company_id = latest.company_id
            AND fr.year = latest.latest_year
        WHERE fr.company_id IN ({placeholders})
    """

    params = company_ids + company_ids

    with get_connection() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=params,
        )


def get_company_names(company_ids: list[str]) -> pd.DataFrame:
    """Return company names for the supplied company IDs."""
    if not company_ids:
        return pd.DataFrame(columns=["company_id", "company_name"])

    placeholders = ",".join("?" for _ in company_ids)

    query = f"""
    SELECT id AS company_id, company_name
    FROM companies
    WHERE id IN ({placeholders})
"""

    with get_connection() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=company_ids,
        )


# ============================================================
# PEER COMPARISON
# ============================================================


def peer_comparison(
    company_id: str,
) -> pd.DataFrame:
    """
    Build a peer-comparison table for a company.

    The selected company and all companies in its peer group
    are compared using their latest financial-ratio records.

    The benchmark company is identified from peer_groups.is_benchmark.
    """

    company_id = str(company_id).strip().upper()

    peer_group_name = get_peer_group(company_id)

    if peer_group_name is None:
        raise ValueError(f"Company '{company_id}' is not assigned to a peer group.")

    peers = get_peer_companies(peer_group_name)

    if peers.empty:
        raise ValueError(f"No companies found for peer group '{peer_group_name}'.")

    company_ids = peers["company_id"].astype(str).tolist()

    ratios = get_latest_financial_ratios(company_ids)

    if ratios.empty:
        raise ValueError(
            f"No financial-ratio data found for peer group " f"'{peer_group_name}'."
        )

    names = get_company_names(company_ids)

    result = peers.merge(
        names,
        on="company_id",
        how="left",
    ).merge(
        ratios,
        on="company_id",
        how="left",
    )

    result["selected_company"] = result["company_id"].str.upper() == company_id

    result["peer_group_name"] = peer_group_name

    # Keep useful columns first.
    preferred_columns = [
        "peer_group_name",
        "company_id",
        "company_name",
        "is_benchmark",
        "selected_company",
        "year",
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "earnings_per_share",
        "book_value_per_share",
        "dividend_payout_ratio_pct",
        "composite_quality_score",
    ]

    available_columns = [
        column for column in preferred_columns if column in result.columns
    ]

    return (
        result[available_columns]
        .sort_values(
            by=["selected_company", "is_benchmark", "company_id"],
            ascending=[False, False, True],
        )
        .reset_index(drop=True)
    )


# ============================================================
# RANKING
# ============================================================


def add_peer_ranks(
    comparison: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add within-peer-group ranks for supported financial metrics.

    Rank 1 means the strongest result according to the metric.
    """
    result = comparison.copy()

    for metric in HIGHER_IS_BETTER:
        if metric in result.columns:
            result[f"{metric}_rank"] = result[metric].rank(
                ascending=False,
                method="min",
            )

    for metric in LOWER_IS_BETTER:
        if metric in result.columns:
            result[f"{metric}_rank"] = result[metric].rank(
                ascending=True,
                method="min",
            )

    return result


# ============================================================
# SUMMARY
# ============================================================


def peer_summary(company_id: str) -> dict:
    """
    Return a compact summary for a company's peer group.
    """

    comparison = peer_comparison(company_id)
    ranked = add_peer_ranks(comparison)

    selected = ranked[ranked["selected_company"] == True]

    if selected.empty:
        raise ValueError(
            f"Company '{company_id}' was not found in its peer comparison."
        )

    selected_row = selected.iloc[0]

    benchmark = ranked[ranked["is_benchmark"] == 1]

    benchmark_company = None

    if not benchmark.empty:
        benchmark_company = benchmark.iloc[0]["company_id"]

    rank_columns = [column for column in ranked.columns if column.endswith("_rank")]

    ranks = {}

    for column in rank_columns:
        value = selected_row[column]

        if pd.notna(value):
            ranks[column.removesuffix("_rank")] = int(value)

    return {
        "company_id": company_id,
        "peer_group_name": selected_row["peer_group_name"],
        "peer_count": len(ranked),
        "benchmark_company": benchmark_company,
        "latest_year": (
            selected_row["year"] if pd.notna(selected_row["year"]) else None
        ),
        "composite_quality_score": (
            float(selected_row["composite_quality_score"])
            if (
                "composite_quality_score" in selected_row
                and pd.notna(selected_row["composite_quality_score"])
            )
            else None
        ),
        "ranks": ranks,
    }
