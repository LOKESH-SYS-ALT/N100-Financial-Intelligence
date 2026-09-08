import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from src.dashboard.utils.db import get_sectors

st.set_page_config(
    page_title="Sectors",
    page_icon="🏭",
    layout="wide",
)

st.title("🏭 Sector Analysis")
st.caption(
    "Explore Nifty 100 companies by sector, market-cap category " "and index weight."
)

sectors = get_sectors()

if sectors.empty:
    st.error("No sector data found.")
    st.stop()


# ---------------------------------------------------------
# Prepare data
# ---------------------------------------------------------

sectors = sectors.copy()

if "index_weight_pct" in sectors.columns:
    sectors["index_weight_pct"] = pd.to_numeric(
        sectors["index_weight_pct"],
        errors="coerce",
    )

if "market_cap_category" in sectors.columns:
    sectors["market_cap_category"] = (
        sectors["market_cap_category"].fillna("Unknown").astype(str)
    )

if "broad_sector" in sectors.columns:
    sectors["broad_sector"] = sectors["broad_sector"].fillna("Unknown").astype(str)


# ---------------------------------------------------------
# Filters
# ---------------------------------------------------------

st.markdown("### 🔎 Filters")

sector_options = sorted(sectors["broad_sector"].dropna().unique().tolist())

selected_sector = st.selectbox(
    "Select Sector",
    ["All Sectors"] + sector_options,
)

filtered = sectors.copy()

if selected_sector != "All Sectors":
    filtered = filtered[filtered["broad_sector"] == selected_sector]


# ---------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------

st.markdown("### 📊 Sector Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Companies",
        len(filtered),
    )

with col2:
    sector_count = filtered["broad_sector"].nunique()
    st.metric(
        "Sectors",
        sector_count,
    )

with col3:
    if "index_weight_pct" in filtered.columns:
        total_weight = filtered["index_weight_pct"].sum()
        st.metric(
            "Index Weight",
            f"{total_weight:.2f}%",
        )
    else:
        st.metric(
            "Index Weight",
            "N/A",
        )

with col4:
    if "market_cap_category" in filtered.columns:
        categories = filtered["market_cap_category"].nunique()
        st.metric(
            "Market Cap Categories",
            categories,
        )
    else:
        st.metric(
            "Market Cap Categories",
            "N/A",
        )


# ---------------------------------------------------------
# Sector Distribution
# ---------------------------------------------------------

st.markdown("### 📈 Companies by Sector")

sector_counts = filtered["broad_sector"].value_counts().sort_values(ascending=False)

if not sector_counts.empty:
    st.bar_chart(
        sector_counts,
        use_container_width=True,
    )
else:
    st.info("No sector distribution available.")


# ---------------------------------------------------------
# Index Weight
# ---------------------------------------------------------

if "index_weight_pct" in filtered.columns:

    st.markdown("### ⚖️ Index Weight by Sector")

    sector_weights = (
        filtered.groupby("broad_sector")["index_weight_pct"]
        .sum()
        .sort_values(ascending=False)
    )

    if not sector_weights.empty:
        st.bar_chart(
            sector_weights,
            use_container_width=True,
        )


# ---------------------------------------------------------
# Market Cap Categories
# ---------------------------------------------------------

if "market_cap_category" in filtered.columns:

    st.markdown("### 💰 Market Cap Category")

    category_counts = (
        filtered["market_cap_category"].value_counts().sort_values(ascending=False)
    )

    if not category_counts.empty:
        st.bar_chart(
            category_counts,
            use_container_width=True,
        )


# ---------------------------------------------------------
# Sector Data Table
# ---------------------------------------------------------

st.markdown("### 📋 Sector Data")

display_columns = [
    "id",
    "company_id",
    "broad_sector",
    "sub_sector",
    "index_weight_pct",
    "market_cap_category",
]

display_columns = [column for column in display_columns if column in filtered.columns]

if display_columns:
    st.dataframe(
        filtered[display_columns],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# Export
# ---------------------------------------------------------

st.markdown("### 📥 Export")

csv_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Sector Data CSV",
    data=csv_data,
    file_name="nifty100_sector_analysis.csv",
    mime="text/csv",
)
