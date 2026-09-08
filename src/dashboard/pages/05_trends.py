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
)

st.set_page_config(
    page_title="Trends",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Financial Trends")
st.caption(
    "Analyze historical financial performance, profitability, "
    "growth and cash-flow trends."
)

companies = get_companies()

if companies.empty:
    st.error("No companies found.")
    st.stop()

company_ids = companies["id"].dropna().astype(str).tolist()

selected_ticker = st.selectbox(
    "Select Company",
    company_ids,
)

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

ratios = get_ratios(selected_ticker)
pl = get_pl(selected_ticker)

if ratios.empty:
    st.warning(f"No financial ratio data found for {selected_ticker}.")
else:

    ratios = ratios.copy()

    if "year" in ratios.columns:
        ratios["year"] = ratios["year"].astype(str)

    st.markdown("### 📊 Profitability & Growth Trends")

    metric_options = [
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "return_on_assets_pct",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
    ]

    available_metrics = [
        metric for metric in metric_options if metric in ratios.columns
    ]

    if available_metrics:

        selected_metrics = st.multiselect(
            "Select metrics",
            available_metrics,
            default=available_metrics[:3],
        )

        if selected_metrics:

            chart_df = ratios[["year"] + selected_metrics].copy()

            for metric in selected_metrics:
                chart_df[metric] = pd.to_numeric(
                    chart_df[metric],
                    errors="coerce",
                )

            chart_df = chart_df.dropna(
                subset=selected_metrics,
                how="all",
            )

            if not chart_df.empty:
                chart_df = chart_df.set_index("year")

                st.line_chart(
                    chart_df,
                    use_container_width=True,
                )

    st.markdown("### 💰 Cash Flow Trend")

    cashflow_columns = [
        "free_cash_flow_cr",
        "cash_from_operations_cr",
        "capex_cr",
    ]

    available_cashflow = [
        column for column in cashflow_columns if column in ratios.columns
    ]

    if available_cashflow:

        cashflow_df = ratios[["year"] + available_cashflow].copy()

        for column in available_cashflow:
            cashflow_df[column] = pd.to_numeric(
                cashflow_df[column],
                errors="coerce",
            )

        cashflow_df = cashflow_df.dropna(
            subset=available_cashflow,
            how="all",
        )

        if not cashflow_df.empty:

            cashflow_df = cashflow_df.set_index("year")

            st.line_chart(
                cashflow_df,
                use_container_width=True,
            )

    st.markdown("### 📋 Historical Ratio Data")

    display_columns = [
        "year",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "free_cash_flow_cr",
        "earnings_per_share",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score",
    ]

    display_columns = [column for column in display_columns if column in ratios.columns]

    if display_columns:
        st.dataframe(
            ratios[display_columns],
            use_container_width=True,
            hide_index=True,
        )

st.markdown("### 📈 Profit & Loss History")

if pl.empty:
    st.info("No P&L data available.")
else:
    st.dataframe(
        pl,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = pl.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download P&L CSV",
        data=csv_data,
        file_name=f"{selected_ticker}_pnl_history.csv",
        mime="text/csv",
    )
