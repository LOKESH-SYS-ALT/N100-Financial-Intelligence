import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from src.dashboard.utils.db import get_companies

from src.analytics.peer_comparison import (
    peer_comparison,
    add_peer_ranks,
    peer_summary,
)

st.set_page_config(
    page_title="Peer Comparison",
    page_icon="👥",
    layout="wide",
)

st.title("👥 Peer Comparison")
st.caption("Compare a Nifty 100 company against companies " "in the same peer group.")

companies = get_companies()

if companies.empty:
    st.error("No companies found.")
    st.stop()

from src.dashboard.utils.db import get_companies
from src.analytics.peer_comparison import (
    peer_comparison,
    add_peer_ranks,
    peer_summary,
)

companies = get_companies()

peer_company_ids = []

for company_id in companies["id"].dropna().astype(str):
    try:
        peer_df = peer_comparison(company_id)
        if not peer_df.empty:
            peer_company_ids.append(company_id)
    except Exception:
        pass

company_ids = peer_company_ids

selected_ticker = st.selectbox(
    "Select Company",
    company_ids,
)

try:
    peers = peer_comparison(selected_ticker)
except Exception as error:
    st.error(f"Unable to load peer comparison: {error}")
    st.stop()

if peers.empty:
    st.warning(f"No peer comparison data found for {selected_ticker}.")
    st.stop()

try:
    ranked = add_peer_ranks(peers)
except Exception as error:
    st.error(f"Unable to calculate rankings: {error}")
    st.stop()

try:
    summary = peer_summary(selected_ticker)
except Exception:
    summary = {}

peer_group_name = summary.get("peer_group_name", "N/A")
peer_count = summary.get("peer_count", len(ranked))
benchmark_company = summary.get(
    "benchmark_company",
    selected_ticker,
)

st.markdown("### 📊 Peer Group Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Peer Group", str(peer_group_name))

with col2:
    st.metric("Companies", str(peer_count))

with col3:
    st.metric("Benchmark", str(benchmark_company))

st.markdown("### 🏆 Company Ranking")

ranks = summary.get("ranks", {})

if ranks:
    rank_rows = []

    for metric, rank in ranks.items():
        if pd.notna(rank):
            rank_rows.append(
                {
                    "Metric": metric,
                    "Rank": int(rank),
                }
            )

    if rank_rows:
        rank_df = pd.DataFrame(rank_rows)

        st.dataframe(
            rank_df,
            use_container_width=True,
            hide_index=True,
        )
else:
    st.info("No individual metric rankings available.")

st.markdown("### 📈 Peer Comparison")

preferred_columns = [
    "company_id",
    "company_name",
    "peer_group_name",
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
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "composite_quality_score",
]

display_columns = [column for column in preferred_columns if column in ranked.columns]

if display_columns:
    st.dataframe(
        ranked[display_columns],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.dataframe(
        ranked,
        use_container_width=True,
        hide_index=True,
    )

st.markdown("### 📥 Export")

csv_data = ranked.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Peer Comparison CSV",
    data=csv_data,
    file_name=f"{selected_ticker}_peer_comparison.csv",
    mime="text/csv",
)
