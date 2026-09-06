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
)


st.set_page_config(
    page_title="Capital Allocation",
    page_icon="💰",
    layout="wide",
)

st.title("💰 Capital Allocation")
st.caption(
    "Analyze free cash flow, capital expenditure, cash generation "
    "and shareholder distribution metrics."
)


# ---------------------------------------------------------
# Company Selection
# ---------------------------------------------------------

companies = get_companies()

if companies.empty:
    st.error("No companies found.")
    st.stop()

company_ids = (
    companies["id"]
    .dropna()
    .astype(str)
    .tolist()
)

selected_ticker = st.selectbox(
    "Select Company",
    company_ids,
)


# ---------------------------------------------------------
# Load Ratios
# ---------------------------------------------------------

ratios = get_ratios(selected_ticker)

if ratios.empty:
    st.warning(
        f"No financial data found for {selected_ticker}."
    )
    st.stop()

ratios = ratios.copy()

if "year" in ratios.columns:
    ratios["year"] = ratios["year"].astype(str)


# ---------------------------------------------------------
# Latest Data
# ---------------------------------------------------------

capital_columns = [
    "free_cash_flow_cr",
    "cash_from_operations_cr",
    "capex_cr",
    "dividend_payout_ratio_pct",
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
]

available_capital_columns = [
    column
    for column in capital_columns
    if column in ratios.columns
]

if available_capital_columns:
    valid_rows = ratios.dropna(
        subset=available_capital_columns,
        how="all",
    )

    if not valid_rows.empty:
        latest = valid_rows.iloc[-1]
    else:
        latest = ratios.iloc[-1]
else:
    latest = ratios.iloc[-1]
def get_value(column):
    if column not in latest.index:
        return None

    value = pd.to_numeric(
        pd.Series([latest[column]]),
        errors="coerce",
    ).iloc[0]

    return value


fcf = get_value("free_cash_flow_cr")
capex = get_value("capex_cr")
cfo = get_value("cash_from_operations_cr")
dividend_payout = get_value("dividend_payout_ratio_pct")
roe = get_value("return_on_equity_pct")
roce = get_value("return_on_capital_employed_pct")


# ---------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------

st.markdown("### 📊 Capital Allocation Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if pd.notna(fcf):
        st.metric(
            "Free Cash Flow",
            f"₹{fcf:,.2f} Cr",
        )
    else:
        st.metric(
            "Free Cash Flow",
            "N/A",
        )

with col2:
    if pd.notna(cfo):
        st.metric(
            "Cash from Operations",
            f"₹{cfo:,.2f} Cr",
        )
    else:
        st.metric(
            "Cash from Operations",
            "N/A",
        )

with col3:
    if pd.notna(capex):
        st.metric(
            "Capital Expenditure",
            f"₹{capex:,.2f} Cr",
        )
    else:
        st.metric(
            "Capital Expenditure",
            "N/A",
        )

with col4:
    if pd.notna(dividend_payout):
        st.metric(
            "Dividend Payout",
            f"{dividend_payout:.2f}%",
        )
    else:
        st.metric(
            "Dividend Payout",
            "N/A",
        )


# ---------------------------------------------------------
# Capital Efficiency
# ---------------------------------------------------------

st.markdown("### 🎯 Capital Efficiency")

col1, col2, col3 = st.columns(3)

with col1:
    if pd.notna(roe):
        st.metric(
            "ROE",
            f"{roe:.2f}%",
        )
    else:
        st.metric(
            "ROE",
            "N/A",
        )

with col2:
    if pd.notna(roce):
        st.metric(
            "ROCE",
            f"{roce:.2f}%",
        )
    else:
        st.metric(
            "ROCE",
            "N/A",
        )

with col3:
    if (
        pd.notna(fcf)
        and pd.notna(cfo)
        and cfo != 0
    ):
        fcf_conversion = (fcf / cfo) * 100

        st.metric(
            "FCF / Operating Cash Flow",
            f"{fcf_conversion:.2f}%",
        )
    else:
        st.metric(
            "FCF / Operating Cash Flow",
            "N/A",
        )


# ---------------------------------------------------------
# Historical Capital Allocation
# ---------------------------------------------------------

st.markdown("### 📈 Historical Capital Allocation")

history_columns = [
    "year",
    "cash_from_operations_cr",
    "capex_cr",
    "free_cash_flow_cr",
    "dividend_payout_ratio_pct",
]

available_columns = [
    column
    for column in history_columns
    if column in ratios.columns
]

if len(available_columns) > 1:

    history = ratios[
        available_columns
    ].copy()

    for column in available_columns:
        if column != "year":
            history[column] = pd.to_numeric(
                history[column],
                errors="coerce",
            )

    history = history.dropna(
        subset=[
            column
            for column in available_columns
            if column != "year"
        ],
        how="all",
    )

    if not history.empty:

        chart_data = history.set_index("year")

        st.line_chart(
            chart_data,
            use_container_width=True,
        )

        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True,
        )

else:
    st.info(
        "Historical capital allocation data is not available."
    )


# ---------------------------------------------------------
# Capital Allocation Interpretation
# ---------------------------------------------------------

st.markdown("### 🧠 Capital Allocation Signals")

signals = []

if pd.notna(fcf):
    if fcf > 0:
        signals.append(
            "✅ Positive free cash flow"
        )
    else:
        signals.append(
            "⚠️ Negative free cash flow"
        )

if pd.notna(cfo) and pd.notna(fcf):
    if cfo > 0 and fcf > 0:
        signals.append(
            "✅ Operating cash generation supports free cash flow"
        )

if pd.notna(dividend_payout):
    if dividend_payout <= 50:
        signals.append(
            "✅ Moderate dividend payout"
        )
    elif dividend_payout <= 80:
        signals.append(
            "🟡 Higher dividend payout"
        )
    else:
        signals.append(
            "⚠️ Very high dividend payout"
        )

if pd.notna(roe):
    if roe >= 15:
        signals.append(
            "✅ ROE indicates strong capital efficiency"
        )
    else:
        signals.append(
            "🟡 ROE is below the 15% reference level"
        )

if signals:
    for signal in signals:
        st.write(signal)
else:
    st.info(
        "No capital allocation signals available."
    )


# ---------------------------------------------------------
# Export
# ---------------------------------------------------------

st.markdown("### 📥 Export")

export_data = ratios.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Capital Allocation CSV",
    data=export_data,
    file_name=f"{selected_ticker}_capital_allocation.csv",
    mime="text/csv",
)