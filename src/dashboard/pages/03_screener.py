import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from src.screener.engine import (
    load_config,
    run_preset,
    run_screener,
)

config = load_config()
PRESETS = config.get("presets", {})


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Screener",
    page_icon="🎯",
    layout="wide",
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🎯 Stock Screener")
st.caption(
    "Screen Nifty 100 companies using predefined strategies "
    "or custom financial filters."
)


# --------------------------------------------------
# Mode Selection
# --------------------------------------------------

mode = st.radio(
    "Screening Mode",
    [
        "Preset Screener",
        "Custom Screener",
    ],
    horizontal=True,
)


# ==================================================
# PRESET SCREENER
# ==================================================

if mode == "Preset Screener":

    st.subheader("📋 Investment Presets")

    preset_names = list(PRESETS.keys())

    if not preset_names:
        st.error("No screener presets found.")
        st.stop()

    selected_preset = st.selectbox(
        "Select Preset",
        preset_names,
    )

    preset_descriptions = {
        "quality_compounder": "High-quality companies with strong profitability and growth.",
        "value_pick": "Companies selected using valuation-oriented filters.",
        "growth_accelerator": "Companies showing strong growth characteristics.",
        "dividend_champion": "Companies with attractive dividend characteristics.",
        "debt_free_blue_chip": "High-quality companies with very low or zero leverage.",
        "turnaround_watch": "Companies showing potential turnaround characteristics.",
    }

    description = preset_descriptions.get(
        selected_preset,
        "Configured investment screening strategy.",
    )

    st.info(description)

    # ----------------------------------------------
    # Run Preset
    # ----------------------------------------------

    try:
        results = run_preset(selected_preset)
    except Exception as error:
        st.error(f"Unable to run preset '{selected_preset}': {error}")
        st.stop()

    if results is None:
        st.error("Screener returned no result.")
        st.stop()

    results = results.copy()

    st.metric(
        "Companies Found",
        len(results),
    )

    # ----------------------------------------------
    # Result Columns
    # ----------------------------------------------

    preferred_columns = [
        "company_id",
        "company_name",
        "broad_sector",
        "market_cap_cr",
        "sales",
        "return_on_equity_pct",
        "operating_profit_margin_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "interest_coverage",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "free_cash_flow_cr",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct",
        "composite_quality_score",
    ]

    display_columns = [
        column for column in preferred_columns if column in results.columns
    ]

    if display_columns:
        st.dataframe(
            results[display_columns],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.dataframe(
            results,
            use_container_width=True,
            hide_index=True,
        )

    # ----------------------------------------------
    # CSV Export
    # ----------------------------------------------

    st.markdown("### 📥 Export")

    csv_data = results.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Results as CSV",
        data=csv_data,
        file_name=f"{selected_preset}_results.csv",
        mime="text/csv",
    )


# ==================================================
# CUSTOM SCREENER
# ==================================================

else:

    st.subheader("⚙️ Custom Screener")

    st.caption(
        "Set any combination of financial filters. "
        "Leave a filter blank to ignore it."
    )

    # ----------------------------------------------
    # Profitability
    # ----------------------------------------------

    st.markdown("### 📊 Profitability")

    c1, c2, c3 = st.columns(3)

    with c1:
        roe_min = st.number_input(
            "Minimum ROE (%)",
            min_value=0.0,
            max_value=200.0,
            value=0.0,
            step=1.0,
        )

    with c2:
        opm_min = st.number_input(
            "Minimum Operating Margin (%)",
            min_value=0.0,
            max_value=200.0,
            value=0.0,
            step=1.0,
        )

    with c3:
        npm_min = st.number_input(
            "Minimum Net Profit Margin (%)",
            min_value=0.0,
            max_value=200.0,
            value=0.0,
            step=1.0,
        )

    # ----------------------------------------------
    # Leverage & Coverage
    # ----------------------------------------------

    st.markdown("### 🏦 Leverage & Coverage")

    c1, c2 = st.columns(2)

    with c1:
        debt_to_equity_max = st.number_input(
            "Maximum Debt / Equity",
            min_value=0.0,
            max_value=20.0,
            value=20.0,
            step=0.1,
        )

    with c2:
        interest_coverage_min = st.number_input(
            "Minimum Interest Coverage",
            min_value=0.0,
            max_value=1000.0,
            value=0.0,
            step=1.0,
        )

    # ----------------------------------------------
    # Growth
    # ----------------------------------------------

    st.markdown("### 🚀 Growth")

    c1, c2, c3 = st.columns(3)

    with c1:
        revenue_cagr_min = st.number_input(
            "Minimum Revenue CAGR 5Y (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0,
        )

    with c2:
        pat_cagr_min = st.number_input(
            "Minimum PAT CAGR 5Y (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0,
        )

    with c3:
        eps_cagr_min = st.number_input(
            "Minimum EPS CAGR 5Y (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0,
        )

    # ----------------------------------------------
    # Cash Flow & Sales
    # ----------------------------------------------

    st.markdown("### 💰 Cash Flow & Sales")

    c1, c2 = st.columns(2)

    with c1:
        fcf_min = st.number_input(
            "Minimum Free Cash Flow (Cr)",
            min_value=0.0,
            max_value=1000000.0,
            value=0.0,
            step=100.0,
        )

    with c2:
        sales_min = st.number_input(
            "Minimum Sales (Cr)",
            min_value=0.0,
            max_value=1000000.0,
            value=0.0,
            step=100.0,
        )

    # ----------------------------------------------
    # Valuation
    # ----------------------------------------------

    st.markdown("### 💎 Valuation")

    c1, c2, c3 = st.columns(3)

    with c1:
        pe_max = st.number_input(
            "Maximum P/E",
            min_value=0.0,
            max_value=1000.0,
            value=1000.0,
            step=1.0,
        )

    with c2:
        pb_max = st.number_input(
            "Maximum P/B",
            min_value=0.0,
            max_value=200.0,
            value=200.0,
            step=1.0,
        )

    with c3:
        dividend_yield_min = st.number_input(
            "Minimum Dividend Yield (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.5,
        )

    # ----------------------------------------------
    # Run Custom Screener
    # ----------------------------------------------

    run_button = st.button(
        "🔎 Run Custom Screener",
        type="primary",
    )

    if run_button:

        filters = {}

        if roe_min > 0:
            filters["roe_min"] = roe_min

        if opm_min > 0:
            filters["opm_min"] = opm_min

        if npm_min > 0:
            filters["npm_min"] = npm_min

        if debt_to_equity_max < 20:
            filters["debt_to_equity_max"] = debt_to_equity_max

        if interest_coverage_min > 0:
            filters["interest_coverage_min"] = interest_coverage_min

        if revenue_cagr_min > 0:
            filters["revenue_cagr_5yr_min"] = revenue_cagr_min

        if pat_cagr_min > 0:
            filters["pat_cagr_5yr_min"] = pat_cagr_min

        if eps_cagr_min > 0:
            filters["eps_cagr_5yr_min"] = eps_cagr_min

        if fcf_min > 0:
            filters["fcf_min"] = fcf_min

        if sales_min > 0:
            filters["sales_min"] = sales_min

        if pe_max < 1000:
            filters["pe_max"] = pe_max

        if pb_max < 200:
            filters["pb_max"] = pb_max

        if dividend_yield_min > 0:
            filters["dividend_yield_min"] = dividend_yield_min

        try:
            results = run_screener(filters)
        except Exception as error:
            st.error(f"Custom screener failed: {error}")
            st.stop()

        if results is None:
            st.error("Screener returned no result.")
            st.stop()

        results = results.copy()

        st.success(f"{len(results)} companies matched your filters.")

        preferred_columns = [
            "company_id",
            "company_name",
            "broad_sector",
            "market_cap_cr",
            "sales",
            "return_on_equity_pct",
            "operating_profit_margin_pct",
            "net_profit_margin_pct",
            "debt_to_equity",
            "interest_coverage",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "eps_cagr_5yr",
            "free_cash_flow_cr",
            "pe_ratio",
            "pb_ratio",
            "dividend_yield_pct",
            "composite_quality_score",
        ]

        display_columns = [
            column for column in preferred_columns if column in results.columns
        ]

        if display_columns:
            st.dataframe(
                results[display_columns],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True,
            )

        # ------------------------------------------
        # CSV Export
        # ------------------------------------------

        csv_data = results.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Custom Results CSV",
            data=csv_data,
            file_name="custom_screener_results.csv",
            mime="text/csv",
        )
