import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import pandas as pd
import streamlit as st

from src.dashboard.utils.db import (
    get_companies,
    get_valuation,
)
from src.analytics.valuation import build_valuation_summary

st.set_page_config(
    page_title="Reports",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Reports & Exports")
st.caption("Generate valuation summaries and export financial analytics.")


# ---------------------------------------------------------
# Company Selection
# ---------------------------------------------------------

companies = get_companies()

if companies.empty:
    st.error("No companies found.")
    st.stop()

company_ids = companies["id"].dropna().astype(str).tolist()

selected_ticker = st.selectbox(
    "Select Company",
    company_ids,
)


# ---------------------------------------------------------
# Company Name
# ---------------------------------------------------------

company_row = companies[companies["id"].astype(str) == selected_ticker]

if not company_row.empty:
    company_name = company_row.iloc[0].get(
        "company_name",
        selected_ticker,
    )
else:
    company_name = selected_ticker

st.markdown(f"## {company_name}")
st.caption(f"Ticker: {selected_ticker}")


# ---------------------------------------------------------
# Valuation Data
# ---------------------------------------------------------

all_valuation = build_valuation_summary()

valuation = all_valuation[
    all_valuation["company_id"].astype(str) == selected_ticker
].copy()

if valuation.empty:
    st.warning(f"No valuation data found for {selected_ticker}.")
    st.stop()

latest = valuation.iloc[-1]

# ---------------------------------------------------------
# Latest Valuation
# ---------------------------------------------------------

latest = valuation.iloc[-1]


def numeric_value(column):
    if column not in latest.index:
        return None

    value = pd.to_numeric(
        pd.Series([latest[column]]),
        errors="coerce",
    ).iloc[0]

    return value


# ---------------------------------------------------------
# Valuation Overview
# ---------------------------------------------------------

st.markdown("### 💰 Valuation Overview")

col1, col2, col3, col4 = st.columns(4)

market_cap = numeric_value("market_cap_crore")
pe_ratio = numeric_value("pe_ratio")
pb_ratio = numeric_value("pb_ratio")
ev_ebitda = numeric_value("ev_ebitda")

with col1:
    st.metric(
        "Market Cap",
        (
            f"₹{market_cap:,.2f} Cr"
            if market_cap is not None and pd.notna(market_cap)
            else "N/A"
        ),
    )

with col2:
    st.metric(
        "P/E Ratio",
        f"{pe_ratio:.2f}" if pe_ratio is not None and pd.notna(pe_ratio) else "N/A",
    )

with col3:
    st.metric(
        "P/B Ratio",
        f"{pb_ratio:.2f}" if pb_ratio is not None and pd.notna(pb_ratio) else "N/A",
    )

with col4:
    st.metric(
        "EV / EBITDA",
        f"{ev_ebitda:.2f}" if ev_ebitda is not None and pd.notna(ev_ebitda) else "N/A",
    )


# ---------------------------------------------------------
# Dividend Yield
# ---------------------------------------------------------

dividend_yield = numeric_value("dividend_yield_pct")

if dividend_yield is not None and pd.notna(dividend_yield):
    st.metric(
        "Dividend Yield",
        f"{dividend_yield:.2f}%",
    )
# ---------------------------------------------------------
# Valuation Signals
# ---------------------------------------------------------

st.markdown("### 🎯 Valuation Signals")

fcf_yield = pd.to_numeric(
    pd.Series([latest.get("fcf_yield_pct")]),
    errors="coerce",
).iloc[0]

pe_flag = latest.get("pe_flag", "N/A")
valuation_label = latest.get(
    "valuation_label",
    "N/A",
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "FCF Yield",
        f"{fcf_yield:.2f}%" if pd.notna(fcf_yield) else "N/A",
    )

with col2:
    st.metric(
        "P/E Flag",
        str(pe_flag),
    )

with col3:
    st.metric(
        "Valuation",
        str(valuation_label),
    )

# ---------------------------------------------------------
# Historical Valuation
# ---------------------------------------------------------

st.markdown("### 📈 Historical Valuation")

display_columns = [
    "year",
    "market_cap_crore",
    "enterprise_value_crore",
    "pe_ratio",
    "pb_ratio",
    "ev_ebitda",
    "dividend_yield_pct",
    "fcf_yield_pct",
    "pe_flag",
    "valuation_label",
]

display_columns = [column for column in display_columns if column in valuation.columns]

if display_columns:
    st.dataframe(
        valuation[display_columns],
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# Valuation Chart
# ---------------------------------------------------------

chart_columns = [
    column
    for column in [
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
    ]
    if column in valuation.columns
]

if chart_columns and "year" in valuation.columns:

    chart_df = valuation[["year"] + chart_columns].copy()

    for column in chart_columns:
        chart_df[column] = pd.to_numeric(
            chart_df[column],
            errors="coerce",
        )

    chart_df = chart_df.set_index("year")

    st.markdown("### 📊 Valuation Multiples")

    st.line_chart(
        chart_df,
        use_container_width=True,
    )


# ---------------------------------------------------------
# CSV Export
# ---------------------------------------------------------

st.markdown("### 📥 Export")

csv_data = valuation.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Valuation CSV",
    data=csv_data,
    file_name=f"{selected_ticker}_valuation.csv",
    mime="text/csv",
)
