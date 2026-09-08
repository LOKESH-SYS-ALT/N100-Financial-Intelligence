import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard.utils.db import (
    get_companies,
    get_ratios,
    get_valuation,
    get_sectors,
)

st.set_page_config(
    page_title="Nifty 100 Analytics",
    layout="wide",
)


st.title("🏠 Nifty 100 Analytics")
st.caption("Nifty 100 financial intelligence dashboard")


# --------------------------------------------------
# Sidebar Year Filter
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

selected_year = st.sidebar.selectbox(
    "Select Year",
    list(range(2019, 2025)),
    index=5,
)


# --------------------------------------------------
# Load Companies
# --------------------------------------------------

companies = get_companies()

if companies.empty:
    st.error("No company data available.")
    st.stop()


# --------------------------------------------------
# Build Ratio Dataset
# --------------------------------------------------

ratio_frames = []

for ticker in companies["id"].dropna().astype(str):
    try:
        df = get_ratios(ticker, selected_year)

        if not df.empty:
            ratio_frames.append(df)

    except Exception as error:
        st.warning(f"Valuation load failed for {ticker}: {error}")
        continue


if ratio_frames:
    ratios = pd.concat(
        ratio_frames,
        ignore_index=True,
    )
else:
    ratios = pd.DataFrame()


# --------------------------------------------------
# Build Valuation Dataset
# --------------------------------------------------

valuation_frames = []

for ticker in companies["id"].dropna().astype(str):
    try:
        df = get_valuation(ticker, selected_year)

        if not df.empty:
            valuation_frames.append(df)

    except Exception:
        continue


if valuation_frames:
    valuation = pd.concat(
        valuation_frames,
        ignore_index=True,
    )
else:
    valuation = pd.DataFrame()


# --------------------------------------------------
# KPI Helpers
# --------------------------------------------------


def safe_median(df, column):
    if column not in df.columns:
        return None

    values = pd.to_numeric(
        df[column],
        errors="coerce",
    ).dropna()

    if values.empty:
        return None

    return values.median()


def safe_mean(df, column):
    if column not in df.columns:
        return None

    values = pd.to_numeric(
        df[column],
        errors="coerce",
    ).dropna()

    if values.empty:
        return None

    return values.mean()


def fmt_number(value, suffix=""):
    if value is None:
        return "N/A"

    return f"{value:.2f}{suffix}"


# --------------------------------------------------
# KPI Calculations
# --------------------------------------------------

average_roe = (
    pd.to_numeric(
        ratios["return_on_equity_pct"],
        errors="coerce",
    ).mean()
    if "return_on_equity_pct" in ratios.columns
    else None
)

median_de = (
    pd.to_numeric(
        ratios["debt_to_equity"],
        errors="coerce",
    ).median()
    if "debt_to_equity" in ratios.columns
    else None
)

median_revenue_cagr = (
    pd.to_numeric(
        ratios["revenue_cagr_5yr"],
        errors="coerce",
    ).median()
    if "revenue_cagr_5yr" in ratios.columns
    else None
)

median_pe = (
    pd.to_numeric(
        valuation["pe_ratio"],
        errors="coerce",
    ).median()
    if "pe_ratio" in valuation.columns
    else None
)

total_companies = len(companies)

debt_free_count = 0

if "debt_to_equity" in ratios.columns:
    debt_values = pd.to_numeric(
        ratios["debt_to_equity"],
        errors="coerce",
    )

    debt_free_count = int((debt_values <= 0).sum())


# --------------------------------------------------
# KPI Tiles
# --------------------------------------------------

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        "Average ROE",
        "N/A" if pd.isna(average_roe) else f"{average_roe:.2f}%",
    )

with col2:
    st.metric(
        "Median P/E",
        "N/A" if pd.isna(median_pe) else f"{median_pe:.2f}",
    )

with col3:
    st.metric(
        "Median D/E",
        "N/A" if pd.isna(median_de) else f"{median_de:.2f}",
    )

with col4:
    st.metric(
        "Total Companies",
        str(total_companies),
    )

with col5:
    st.metric(
        "Median Revenue CAGR",
        ("N/A" if pd.isna(median_revenue_cagr) else f"{median_revenue_cagr:.2f}%"),
    )

with col6:
    st.metric(
        "Debt-Free Companies",
        str(debt_free_count),
    )


# --------------------------------------------------
# Diagnostic
# --------------------------------------------------

st.caption(
    f"Dashboard data: {len(ratios)} ratio rows | "
    f"{len(valuation)} valuation rows | "
    f"Year: {selected_year}"
)


# --------------------------------------------------
# Sector Breakdown
# --------------------------------------------------

st.subheader("📊 Sector Breakdown")


try:
    sectors = get_sectors()

    if not sectors.empty and "broad_sector" in sectors.columns:

        sector_counts = (
            sectors.groupby("broad_sector")
            .size()
            .reset_index(name="company_count")
            .sort_values(
                "company_count",
                ascending=False,
            )
        )

        fig = px.pie(
            sector_counts,
            names="broad_sector",
            values="company_count",
            hole=0.45,
            title="Nifty 100 Companies by Sector",
        )

        fig.update_layout(
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:
        st.info("Sector data is not available.")

except Exception as error:
    st.warning(f"Unable to load sector breakdown: {error}")


# --------------------------------------------------
# Top 5 Quality Companies
# --------------------------------------------------

st.subheader("🏆 Top 5 Companies by Composite Quality Score")


if not ratios.empty:

    top_columns = [
        "company_id",
        "company_name",
        "composite_quality_score",
    ]

    available_columns = [column for column in top_columns if column in ratios.columns]

    top5 = ratios[available_columns].copy()

    if "composite_quality_score" in top5.columns:

        top5["composite_quality_score"] = pd.to_numeric(
            top5["composite_quality_score"],
            errors="coerce",
        )

        top5 = (
            top5.dropna(subset=["composite_quality_score"])
            .sort_values(
                "composite_quality_score",
                ascending=False,
            )
            .head(5)
        )

        st.dataframe(
            top5,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("Composite quality score is not available.")

else:
    st.info(f"No ratio data available for {selected_year}.")


# --------------------------------------------------
# Data Availability
# --------------------------------------------------

st.caption(
    f"Loaded {len(ratios)} company ratio records and "
    f"{len(valuation)} valuation records for {selected_year}."
)
