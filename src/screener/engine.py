"""
N100 Financial Intelligence
Sprint 3 - Screener & Peer Comparison Engine

Day 15:
    - Load screener configuration
    - Load latest financial data
    - Apply threshold filters
    - Handle Financials-sector D/E rule
    - Handle debt-free ICR rule
    - Calculate composite quality score
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import sqlite3

import numpy as np
import pandas as pd
import yaml

# ============================================================
# FINANCIAL DATA ALIGNMENT
# ============================================================


def get_latest_common_financial_year(
    pnl: pd.DataFrame,
    balance: pd.DataFrame,
    cashflow: pd.DataFrame,
) -> int | None:
    """
    Find the latest year available across the three
    core financial statements.
    """

    year_sets = []

    for df in [pnl, balance, cashflow]:
        if df.empty or "year" not in df.columns:
            continue

        years = df["year"].apply(normalize_year).dropna().astype(int)

        if not years.empty:
            year_sets.append(set(years.tolist()))

    if not year_sets:
        return None

    common_years = set.intersection(*year_sets)

    if not common_years:
        return None

    return max(common_years)


def latest_common_year_per_company(
    pnl: pd.DataFrame,
    balance: pd.DataFrame,
    cashflow: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Align P&L, Balance Sheet and Cash Flow to the
    latest common financial year for each company.
    """

    if pnl.empty:
        return pnl.copy(), balance.copy(), cashflow.copy()

    pnl = pnl.copy()
    balance = balance.copy()
    cashflow = cashflow.copy()

    for df in [pnl, balance, cashflow]:
        if "year" in df.columns:
            df["_normalized_year"] = df["year"].apply(normalize_year)

    companies = set()

    for df in [pnl, balance, cashflow]:
        if "company_id" in df.columns:
            companies.update(df["company_id"].dropna().astype(str))

    aligned_pnl = []
    aligned_balance = []
    aligned_cashflow = []

    for company_id in companies:

        p = pnl[pnl["company_id"].astype(str) == company_id]
        b = balance[balance["company_id"].astype(str) == company_id]
        cf = cashflow[cashflow["company_id"].astype(str) == company_id]

        p_years = set(p["_normalized_year"].dropna().astype(int))
        b_years = set(b["_normalized_year"].dropna().astype(int))
        cf_years = set(cf["_normalized_year"].dropna().astype(int))

        common = p_years & b_years & cf_years

        if not common:
            continue

        latest_year = max(common)

        aligned_pnl.append(p[p["_normalized_year"] == latest_year].tail(1))

        aligned_balance.append(b[b["_normalized_year"] == latest_year].tail(1))

        aligned_cashflow.append(cf[cf["_normalized_year"] == latest_year].tail(1))

    def combine(parts, original):
        if parts:
            result = pd.concat(
                parts,
                ignore_index=True,
            )
        else:
            result = original.iloc[0:0].copy()

        return result.drop(
            columns=["_normalized_year"],
            errors="ignore",
        )

    return (
        combine(aligned_pnl, pnl),
        combine(aligned_balance, balance),
        combine(aligned_cashflow, cashflow),
    )


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"
CONFIG_PATH = PROJECT_ROOT / "config" / "screener_config.yaml"


# ============================================================
# CONFIG
# ============================================================


def load_config(
    config_path: str | Path = CONFIG_PATH,
) -> dict[str, Any]:
    """Load screener_config.yaml."""

    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Screener config not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    if not isinstance(config, dict):
        raise ValueError("screener_config.yaml must contain a YAML mapping.")

    return config


# ============================================================
# DATABASE HELPERS
# ============================================================


def table_exists(
    connection: sqlite3.Connection,
    table_name: str,
) -> bool:
    """Check whether a SQLite table exists."""

    result = connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        LIMIT 1
        """,
        (table_name,),
    ).fetchone()

    return result is not None


def read_table(
    connection: sqlite3.Connection,
    table_name: str,
) -> pd.DataFrame:
    """Read a SQLite table safely."""

    if not table_exists(connection, table_name):
        return pd.DataFrame()

    return pd.read_sql_query(
        f"SELECT * FROM {table_name}",
        connection,
    )


def clean_duplicate_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove duplicate column labels.

    This prevents pandas merge errors such as:

        ValueError:
        The column label 'company_id' is not unique.
    """

    df = dataframe.copy()

    df = df.loc[:, ~df.columns.duplicated()]

    return df


# ============================================================
# YEAR NORMALISATION
# ============================================================


def normalize_year(value: Any) -> int | None:
    """
    Convert different year formats into an integer year.

    Examples:
        2024       -> 2024
        "2024"     -> 2024
        "Dec 2024" -> 2024
        "FY 2024"  -> 2024
        "Mar-22"   -> 2022
        "Mar-14"   -> 2014
        "TTM"      -> None
    """

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    import re

    # Four-digit year: 2024, Dec 2024, FY 2024
    match = re.search(r"(19|20)\d{2}", text)

    if match:
        try:
            return int(match.group(0))
        except ValueError:
            return None

    # Two-digit year: Mar-22, Mar-14, Mar-13
    match = re.search(r"(?:^|[-/ ])(\d{2})$", text)

    if match:
        try:
            year = int(match.group(1))

            # Financial dataset uses 20xx for these years.
            if 0 <= year <= 30:
                return 2000 + year

            return 1900 + year

        except ValueError:
            return None

    return None


# ============================================================
# LATEST YEAR
# ============================================================


def latest_per_company(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep latest valid year for every company.
    """

    if dataframe.empty:
        return dataframe.copy()

    df = clean_duplicate_columns(dataframe)

    if "company_id" not in df.columns:
        return df

    if "year" in df.columns:
        df["_normalized_year"] = df["year"].apply(normalize_year)

        df = df.sort_values(
            ["company_id", "_normalized_year"],
            na_position="first",
        )

        df = (
            df.groupby(
                "company_id",
                as_index=False,
                sort=False,
            )
            .tail(1)
            .copy()
        )

        df.drop(
            columns=["_normalized_year"],
            inplace=True,
            errors="ignore",
        )

    return df.reset_index(drop=True)


# ============================================================
# SECTOR LOADING
# ============================================================


def prepare_sector_data(
    sectors: pd.DataFrame,
) -> pd.DataFrame:
    """
    Safely identify company_id and sector column
    from the sectors table.
    """

    if sectors.empty:
        return pd.DataFrame(
            columns=[
                "company_id",
                "broad_sector",
            ]
        )

    df = clean_duplicate_columns(sectors)

    # --------------------------------------------------------
    # Find company ID
    # --------------------------------------------------------

    company_column = None

    for candidate in [
        "company_id",
        "id",
        "company",
        "ticker",
    ]:
        if candidate in df.columns:
            company_column = candidate
            break

    if company_column is None:
        return pd.DataFrame(
            columns=[
                "company_id",
                "broad_sector",
            ]
        )

    # --------------------------------------------------------
    # Find sector column
    # --------------------------------------------------------

    sector_column = None

    for candidate in [
        "broad_sector",
        "sector",
        "sector_name",
        "industry",
        "industry_name",
        "category",
    ]:
        if candidate in df.columns:
            sector_column = candidate
            break

    if sector_column is None:
        return pd.DataFrame(
            columns=[
                "company_id",
                "broad_sector",
            ]
        )

    result = df[
        [
            company_column,
            sector_column,
        ]
    ].copy()

    result.rename(
        columns={
            company_column: "company_id",
            sector_column: "broad_sector",
        },
        inplace=True,
    )

    result = clean_duplicate_columns(result)

    result = result.drop_duplicates(subset=["company_id"])

    return result


# ============================================================
# MARKET CAP
# ============================================================


def prepare_market_cap(
    market_cap: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare latest market-cap and valuation data."""

    if market_cap.empty:
        return pd.DataFrame()

    df = clean_duplicate_columns(market_cap).copy()

    # Find company id.
    if "company_id" not in df.columns and "id" in df.columns:
        df.rename(
            columns={"id": "company_id"},
            inplace=True,
        )

    if "company_id" not in df.columns:
        return pd.DataFrame()

    # Normalize actual database column names.
    df.rename(
        columns={
            "market_cap_crore": "market_cap_cr",
            "pe_ratio": "price_to_earnings",
            "pb_ratio": "price_to_book",
            "dividend_yield_pct": "dividend_yield_pct",
        },
        inplace=True,
    )

    # Keep all useful screener valuation columns.
    wanted = [
        "company_id",
        "market_cap_cr",
        "price_to_earnings",
        "price_to_book",
        "dividend_yield_pct",
    ]

    available = [col for col in wanted if col in df.columns]

    if "company_id" not in available:
        return pd.DataFrame()

    if "year" in df.columns:
        available.append("year")

    result = df[list(dict.fromkeys(available))].copy()

    # Normalize year.
    if "year" in result.columns:
        result["_year"] = result["year"].apply(normalize_year)

        # Remove invalid years before sorting.
        result = result[result["_year"].notna()].copy()

        if not result.empty:
            result = (
                result.sort_values(["company_id", "_year"])
                .groupby(
                    "company_id",
                    as_index=False,
                )
                .tail(1)
            )

        result.drop(
            columns=["_year"],
            inplace=True,
            errors="ignore",
        )

    return result.reset_index(drop=True)


# ============================================================
# LOAD SCREENER DATA
# ============================================================


def load_screener_data(
    db_path: str | Path = DB_PATH,
) -> pd.DataFrame:
    """
    Load latest financial data for all companies.

    Primary source:
        financial_ratios

    Additional sources:
        companies
        sectors
        market_cap
        profitandloss
        balancesheet
    """

    path = Path(db_path)

    if not path.exists():
        raise FileNotFoundError(f"Database not found: {path}")

    connection = sqlite3.connect(path)

    try:

        ratios = read_table(
            connection,
            "financial_ratios",
        )

        companies = read_table(
            connection,
            "companies",
        )

        sectors = read_table(
            connection,
            "sectors",
        )

        market_cap = read_table(
            connection,
            "market_cap",
        )

        profit_loss = read_table(
            connection,
            "profitandloss",
        )

        balance_sheet = read_table(
            connection,
            "balancesheet",
        )

    finally:

        connection.close()

    if ratios.empty:
        raise ValueError("financial_ratios table is empty.")

    # --------------------------------------------------------
    # Clean ratios
    # --------------------------------------------------------

    ratios = clean_duplicate_columns(ratios)

    # Keep all historical ratio rows before selecting latest
    all_ratios = ratios.copy()

    ratios = latest_per_company(ratios)

    # --------------------------------------------------------
    # Fill missing latest ratio values from historical data
    # --------------------------------------------------------

    ratio_fill_columns = [
        "return_on_equity_pct",
        "free_cash_flow_cr",
        "dividend_payout_ratio_pct",
        "return_on_capital_employed_pct",
        "cash_from_operations_cr",
        "interest_coverage",
    ]

    if not all_ratios.empty:

        all_ratios["_normalized_year"] = all_ratios["year"].apply(normalize_year)

        all_ratios = all_ratios.sort_values(
            [
                "company_id",
                "_normalized_year",
            ],
            na_position="first",
        )

        for column in ratio_fill_columns:

            if column not in all_ratios.columns:
                continue

            fallback = (
                all_ratios[
                    [
                        "company_id",
                        column,
                    ]
                ]
                .dropna(subset=[column])
                .drop_duplicates(
                    subset=["company_id"],
                    keep="last",
                )
            )

            ratios = ratios.merge(
                fallback,
                on="company_id",
                how="left",
                suffixes=("", "_fallback"),
            )

            fallback_column = f"{column}_fallback"

            if fallback_column in ratios.columns:

                ratios[column] = ratios[column].fillna(ratios[fallback_column])

                ratios.drop(
                    columns=[fallback_column],
                    inplace=True,
                )

    # --------------------------------------------------------
    # Companies
    # --------------------------------------------------------

    if not companies.empty:

        companies = clean_duplicate_columns(companies)

        if "id" in companies.columns:

            company_columns = ["id"]

            if "company_name" in companies.columns:
                company_columns.append("company_name")

            if "website" in companies.columns:
                company_columns.append("website")

            company_df = companies[company_columns].copy()

            company_df.rename(
                columns={"id": "company_id"},
                inplace=True,
            )

            company_df = clean_duplicate_columns(company_df)

            company_df = company_df.drop_duplicates(subset=["company_id"])

            ratios = ratios.merge(
                company_df,
                on="company_id",
                how="left",
                suffixes=("", "_company"),
            )

    # --------------------------------------------------------
    # Sector
    # --------------------------------------------------------

    sector_df = prepare_sector_data(sectors)

    if not sector_df.empty:

        # IMPORTANT:
        # Ensure company_id is unique before merge.
        sector_df = clean_duplicate_columns(sector_df)

        sector_df = sector_df[
            [
                "company_id",
                "broad_sector",
            ]
        ].drop_duplicates(subset=["company_id"])

        ratios = ratios.merge(
            sector_df,
            on="company_id",
            how="left",
        )

    # --------------------------------------------------------
    # Market Cap
    # --------------------------------------------------------

    market_df = prepare_market_cap(market_cap)

    if not market_df.empty:

        ratios = ratios.merge(
            market_df,
            on="company_id",
            how="left",
            suffixes=("", "_market"),
        )

    # --------------------------------------------------------
    # Profit and Loss
    # --------------------------------------------------------

    if not profit_loss.empty:

        pl = clean_duplicate_columns(profit_loss)

        pl = latest_per_company(pl)

        keep_columns = [
            "company_id",
            "sales",
            "net_profit",
            "eps",
            "interest",
            "opm_percentage",
            "dividend_payout",
        ]

        keep_columns = [column for column in keep_columns if column in pl.columns]

        if "company_id" in keep_columns:

            pl = pl[keep_columns]

            pl = pl.drop_duplicates(subset=["company_id"])

            ratios = ratios.merge(
                pl,
                on="company_id",
                how="left",
                suffixes=("", "_pl"),
            )

    # --------------------------------------------------------
    # Balance Sheet
    # --------------------------------------------------------

    if not balance_sheet.empty:

        bs = clean_duplicate_columns(balance_sheet)

        bs = latest_per_company(bs)

        keep_columns = [
            "company_id",
            "borrowings",
            "total_assets",
            "equity_capital",
            "reserves",
        ]

        keep_columns = [column for column in keep_columns if column in bs.columns]

        if "company_id" in keep_columns:

            bs = bs[keep_columns]

            bs = bs.drop_duplicates(subset=["company_id"])

            ratios = ratios.merge(
                bs,
                on="company_id",
                how="left",
                suffixes=("", "_bs"),
            )

    # --------------------------------------------------------
    # Remove temporary/duplicate columns
    # --------------------------------------------------------

    ratios = clean_duplicate_columns(ratios)

    return ratios.reset_index(drop=True)


# ============================================================
# NUMERIC HELPERS
# ============================================================


def numeric(
    series: pd.Series,
) -> pd.Series:
    """Convert values to numeric."""
    return pd.to_numeric(
        series,
        errors="coerce",
    )


def ensure_column(
    dataframe: pd.DataFrame,
    column: str,
    default: Any = np.nan,
) -> None:
    """Create a missing column."""
    if column not in dataframe.columns:
        dataframe[column] = default


# ============================================================
# WINSORISED SCORE
# ============================================================


def winsorized_score(
    series: pd.Series,
    higher_is_better: bool = True,
) -> pd.Series:
    """
    P10/P90 winsorisation and 0-100 scaling.
    """

    values = numeric(series)

    valid = values.dropna()

    if valid.empty:

        return pd.Series(
            np.nan,
            index=series.index,
            dtype=float,
        )

    p10 = valid.quantile(0.10)
    p90 = valid.quantile(0.90)

    if pd.isna(p10) or pd.isna(p90):

        return pd.Series(
            np.nan,
            index=series.index,
            dtype=float,
        )

    if p10 == p90:

        result = pd.Series(
            50.0,
            index=series.index,
            dtype=float,
        )

        result[values.isna()] = np.nan

        return result

    clipped = values.clip(
        lower=p10,
        upper=p90,
    )

    score = ((clipped - p10) / (p90 - p10)) * 100.0

    if not higher_is_better:
        score = 100.0 - score

    return score


# ============================================================
# COMPOSITE SCORE
# ============================================================


def calculate_composite_quality_score(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Composite Quality Score.

    Profitability 35%
    Cash Quality  30%
    Growth        20%
    Leverage      15%
    """

    df = dataframe.copy()

    required_columns = [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "net_profit_margin_pct",
        "free_cash_flow_cr",
        "cash_from_operations_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "debt_to_equity",
        "interest_coverage",
    ]

    for column in required_columns:
        ensure_column(df, column)

    # --------------------------------------------------------
    # Profitability
    # --------------------------------------------------------

    roe_score = winsorized_score(
        df["return_on_equity_pct"],
        higher_is_better=True,
    )

    roce_score = winsorized_score(
        df["return_on_capital_employed_pct"],
        higher_is_better=True,
    )

    npm_score = winsorized_score(
        df["net_profit_margin_pct"],
        higher_is_better=True,
    )
    profitability = (
        roe_score.fillna(50.0) * 0.15
        + roce_score.fillna(50.0) * 0.10
        + npm_score.fillna(50.0) * 0.10
    )
    # --------------------------------------------------------
    # Cash Quality
    # --------------------------------------------------------

    fcf_score = winsorized_score(
        df["free_cash_flow_cr"],
        higher_is_better=True,
    )

    cfo_score = winsorized_score(
        df["cash_from_operations_cr"],
        higher_is_better=True,
    )

    fcf_positive_flag = (numeric(df["free_cash_flow_cr"]) > 0).astype(float) * 100.0

    cash_quality = (
        fcf_score.fillna(50.0) * 0.15
        + cfo_score.fillna(50.0) * 0.10
        + fcf_positive_flag.fillna(50.0) * 0.05
    )

    # --------------------------------------------------------
    # Growth
    # --------------------------------------------------------

    revenue_growth_score = winsorized_score(
        df["revenue_cagr_5yr"],
        higher_is_better=True,
    )

    pat_growth_score = winsorized_score(
        df["pat_cagr_5yr"],
        higher_is_better=True,
    )

    growth = (
        revenue_growth_score.fillna(50.0) * 0.10 + pat_growth_score.fillna(50.0) * 0.10
    )

    # --------------------------------------------------------
    # Leverage
    # --------------------------------------------------------

    de_score = winsorized_score(
        df["debt_to_equity"],
        higher_is_better=False,
    )

    icr_score = winsorized_score(
        df["interest_coverage"],
        higher_is_better=True,
    )

    leverage = de_score.fillna(50.0) * 0.10 + icr_score.fillna(50.0) * 0.05

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    df["composite_quality_score"] = profitability + cash_quality + growth + leverage

    df["composite_quality_score"] = df["composite_quality_score"].clip(0, 100).round(2)

    return df


# ============================================================
# FILTER ENGINE
# ============================================================


def apply_filters(
    dataframe: pd.DataFrame,
    filters: dict[str, Any] | None = None,
    preset_name: str | None = None,
) -> pd.DataFrame:
    """
    Apply screener filters.

    Supported metrics:

        ROE min
        D/E max
        FCF min
        Revenue CAGR 5yr min
        PAT CAGR 5yr min
        OPM min
        P/E max
        P/B max
        Dividend Yield min
        ICR min
        Market Cap min
        Net Profit min
        EPS CAGR min
        Asset Turnover min
        Sales min
    """

    df = dataframe.copy()
    df = calculate_composite_quality_score(df)
    filters = filters or {}

    # --------------------------------------------------------
    # Minimum filters
    # --------------------------------------------------------

    minimum_filters = {
        "roe_min": "return_on_equity_pct",
        "fcf_min": "free_cash_flow_cr",
        "revenue_cagr_5yr_min": "revenue_cagr_5yr",
        "pat_cagr_5yr_min": "pat_cagr_5yr",
        "opm_min": "operating_profit_margin_pct",
        "dividend_yield_min": "dividend_yield_pct",
        "icr_min": "interest_coverage",
        "market_cap_min": "market_cap_cr",
        "net_profit_min": "net_profit",
        "eps_cagr_5yr_min": "eps_cagr_5yr",
        "asset_turnover_min": "asset_turnover",
        "sales_min": "sales",
    }

    # --------------------------------------------------------
    # Maximum filters
    # --------------------------------------------------------

    maximum_filters = {
        "debt_to_equity_max": "debt_to_equity",
        "pe_max": "pe_ratio",
        "pb_max": "pb_ratio",
        "dividend_payout_max": "dividend_payout_ratio_pct",
    }

    # --------------------------------------------------------
    # Apply minimum filters
    # --------------------------------------------------------

    for filter_name, column in minimum_filters.items():

        threshold = filters.get(filter_name)

        if threshold is None:
            continue

        if column not in df.columns:
            continue

        values = numeric(df[column])

        df = df.loc[values >= float(threshold)].copy()

    # --------------------------------------------------------
    # Apply maximum filters
    # --------------------------------------------------------

    for filter_name, column in maximum_filters.items():

        threshold = filters.get(filter_name)

        if threshold is None:
            continue

        if column not in df.columns:
            continue

        values = numeric(df[column])

        df = df.loc[values <= float(threshold)].copy()

    # --------------------------------------------------------
    # Financials D/E rule
    # --------------------------------------------------------

    if (
        filters.get("debt_to_equity_max") is not None
        and preset_name != "debt_free_blue_chip"
    ):

        if "broad_sector" in df.columns:

            sector_text = (
                df["broad_sector"].fillna("").astype(str).str.strip().str.lower()
            )

            financials = sector_text == "financials"

            df = df.loc[~financials].copy()

    # --------------------------------------------------------
    # Debt-free ICR rule
    # --------------------------------------------------------

    if filters.get("icr_min") is not None:

        if "interest_coverage" in df.columns:

            icr = numeric(df["interest_coverage"])

            de = numeric(df["debt_to_equity"])

            debt_free = de.fillna(np.nan) == 0

            passes = (icr >= float(filters["icr_min"])) | debt_free

            df = df.loc[passes].copy()

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    if "composite_quality_score" in df.columns:

        df = df.sort_values(
            "composite_quality_score",
            ascending=False,
            na_position="last",
        )

    return df.reset_index(drop=True)


# ============================================================
# PRESETS
# ============================================================


def get_preset_filters(
    preset_name: str,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Get filters for a preset."""

    if config is None:
        config = load_config()

    presets = config.get("presets", {})

    if preset_name not in presets:

        available = ", ".join(sorted(presets.keys()))

        raise KeyError(
            f"Unknown preset '{preset_name}'. " f"Available presets: {available}"
        )

    preset = presets[preset_name]

    if not isinstance(
        preset,
        dict,
    ):
        return {}

    return dict(preset.get("filters", {}))


def run_preset(
    preset_name: str,
    dataframe: pd.DataFrame | None = None,
    config: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Run one configured preset."""

    if config is None:
        config = load_config()

    if dataframe is None:
        dataframe = load_screener_data()

    filters = get_preset_filters(
        preset_name,
        config,
    )

    return apply_filters(
        dataframe,
        filters,
        preset_name,
    )


# ============================================================
# PUBLIC API
# ============================================================


def run_screener(
    filters: dict[str, Any] | None = None,
    dataframe: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Run a custom screener.

    Example:

        run_screener(
            {
                "roe_min": 15,
                "debt_to_equity_max": 1.0,
            }
        )
    """

    if dataframe is None:
        dataframe = load_screener_data()

    return apply_filters(
        dataframe,
        filters or {},
    )


# ============================================================
# MAIN
# ============================================================


def main() -> None:
    """Day 15 smoke test."""

    print("=" * 60)
    print("N100 FINANCIAL INTELLIGENCE")
    print("SPRINT 3 - SCREENER ENGINE")
    print("=" * 60)

    config = load_config()

    data = load_screener_data()

    print(f"Universe rows: {len(data)}")

    if "company_id" in data.columns:

        print(f"Companies: " f"{data['company_id'].nunique()}")

    print("\nAvailable presets:")

    presets = config.get("presets", {})

    for preset_name, preset in presets.items():

        if isinstance(
            preset,
            dict,
        ):

            display_name = preset.get(
                "name",
                preset_name,
            )

        else:

            display_name = preset_name

        print(f"  - {preset_name}: " f"{display_name}")

    print("\nDay 15 engine loaded successfully.")


if __name__ == "__main__":
    main()
