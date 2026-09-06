import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from src.dashboard.utils.db import (
    get_companies,
    get_ratios,
    get_pl,
    get_bs,
    get_cf,
    get_valuation,
    get_sectors,
)


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Company Profile",
    page_icon="🏢",
    layout="wide",
)


# --------------------------------------------------
# Load Companies
# --------------------------------------------------

companies = get_companies()

if companies.empty:
    st.error("No companies found in the database.")
    st.stop()


# --------------------------------------------------
# Company Selection
# --------------------------------------------------

st.title("🏢 Company Profile")
st.caption("Nifty 100 company financial intelligence")

company_options = companies["id"].dropna().astype(str).tolist()

selected_ticker = st.selectbox(
    "Select Company",
    company_options,
)


# --------------------------------------------------
# Company Details
# --------------------------------------------------

company_row = companies[
    companies["id"].astype(str) == selected_ticker
]

if company_row.empty:
    st.error("Company not found.")
    st.stop()

company = company_row.iloc[0]

company_name = company.get(
    "company_name",
    selected_ticker,
)


# --------------------------------------------------
# Sector
# --------------------------------------------------

sectors = get_sectors()

sector_name = "N/A"

if not sectors.empty and "company_id" in sectors.columns:
    sector_row = sectors[
        sectors["company_id"].astype(str)
        == selected_ticker
    ]

    if not sector_row.empty:
        sector_name = sector_row.iloc[0].get(
            "broad_sector",
            "N/A",
        )


# --------------------------------------------------
# Latest Financial Data
# --------------------------------------------------

ratios = get_ratios(
    selected_ticker,
    2024,
)

valuation = get_valuation(
    selected_ticker,
    2024,
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.subheader(company_name)

st.write(
    f"**Ticker:** {selected_ticker}  |  "
    f"**Sector:** {sector_name}"
)


# --------------------------------------------------
# KPI Helpers
# --------------------------------------------------

def value_from_df(df, column):
    if df.empty or column not in df.columns:
        return None

    value = df.iloc[0][column]

    if pd.isna(value):
        return None

    return float(value)


def fmt(value, suffix=""):
    if value is None:
        return "N/A"

    return f"{value:,.2f}{suffix}"


# --------------------------------------------------
# KPI Values
# --------------------------------------------------

roe = value_from_df(
    ratios,
    "return_on_equity_pct",
)

roce = value_from_df(
    ratios,
    "return_on_capital_employed_pct",
)

debt_to_equity = value_from_df(
    ratios,
    "debt_to_equity",
)

revenue_cagr = value_from_df(
    ratios,
    "revenue_cagr_5yr",
)

pat_cagr = value_from_df(
    ratios,
    "pat_cagr_5yr",
)

eps_cagr = value_from_df(
    ratios,
    "eps_cagr_5yr",
)

pe_ratio = value_from_df(
    valuation,
    "pe_ratio",
)

pb_ratio = value_from_df(
    valuation,
    "pb_ratio",
)

market_cap = value_from_df(
    valuation,
    "market_cap_crore",
)


# --------------------------------------------------
# KPI Cards
# --------------------------------------------------

st.markdown("### 📊 Key Metrics")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "ROE",
        fmt(roe, "%"),
    )

with c2:
    st.metric(
        "ROCE",
        fmt(roce, "%"),
    )

with c3:
    st.metric(
        "Debt / Equity",
        fmt(debt_to_equity),
    )

with c4:
    st.metric(
        "Market Cap",
        (
            "N/A"
            if market_cap is None
            else f"₹{market_cap:,.2f} Cr"
        ),
    )


c5, c6, c7, c8 = st.columns(4)

with c5:
    st.metric(
        "P/E",
        fmt(pe_ratio),
    )

with c6:
    st.metric(
        "P/B",
        fmt(pb_ratio),
    )

with c7:
    st.metric(
        "Revenue CAGR",
        fmt(revenue_cagr, "%"),
    )

with c8:
    st.metric(
        "PAT CAGR",
        fmt(pat_cagr, "%"),
    )


# --------------------------------------------------
# Growth Metrics
# --------------------------------------------------

st.markdown("### 🚀 Growth & Quality")

g1, g2, g3 = st.columns(3)

with g1:
    st.metric(
        "Revenue CAGR (5Y)",
        fmt(revenue_cagr, "%"),
    )

with g2:
    st.metric(
        "PAT CAGR (5Y)",
        fmt(pat_cagr, "%"),
    )

with g3:
    st.metric(
        "EPS CAGR (5Y)",
        fmt(eps_cagr, "%"),
    )


# --------------------------------------------------
# Financial Ratios
# --------------------------------------------------

st.markdown("### 📐 Financial Ratios")

if ratios.empty:
    st.info("No ratio data available.")
else:
    ratio_columns = [
        "year",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "earnings_per_share",
        "book_value_per_share",
        "composite_quality_score",
    ]

    available_columns = [
        column
        for column in ratio_columns
        if column in ratios.columns
    ]

    st.dataframe(
        ratios[available_columns],
        use_container_width=True,
        hide_index=True,
    )


# --------------------------------------------------
# Profit & Loss
# --------------------------------------------------

st.markdown("### 💰 Profit & Loss")

pl = get_pl(selected_ticker)

if pl.empty:
    st.info("No Profit & Loss data available.")
else:
    st.dataframe(
        pl,
        use_container_width=True,
        hide_index=True,
    )


# --------------------------------------------------
# Balance Sheet
# --------------------------------------------------

st.markdown("### 🏦 Balance Sheet")

bs = get_bs(selected_ticker)

if bs.empty:
    st.info("No Balance Sheet data available.")
else:
    st.dataframe(
        bs,
        use_container_width=True,
        hide_index=True,
    )


# --------------------------------------------------
# Cash Flow
# --------------------------------------------------

st.markdown("### 💵 Cash Flow")

cf = get_cf(selected_ticker)

if cf.empty:
    st.info("No Cash Flow data available.")
else:
    st.dataframe(
        cf,
        use_container_width=True,
        hide_index=True,
    )


# --------------------------------------------------
# Company Information
# --------------------------------------------------

st.markdown("### ℹ️ Company Information")

info1, info2 = st.columns(2)

with info1:
    st.write(
        "**Face Value:**",
        company.get("face_value", "N/A"),
    )

    st.write(
        "**Book Value:**",
        company.get("book_value", "N/A"),
    )

with info2:
    website = company.get("website")

    if pd.notna(website) and website:
        st.write(f"**Website:** {website}")

    st.write(
        "**Company ID:**",
        selected_ticker,
    )