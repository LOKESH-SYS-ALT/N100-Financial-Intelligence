import streamlit as st

st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.title("📊 Nifty 100 Financial Intelligence")
st.caption("Financial analytics, screening, peer intelligence and valuation")


st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Home",
        "👤 Company Profile",
        "🔎 Screener",
        "👥 Peer Comparison",
        "📈 Trend Analysis",
        "🏢 Sector Analysis",
        "💰 Capital Allocation",
        "📄 Annual Reports",
    ],
)


if page == "🏠 Home":
    st.header("🏠 Home")
    st.info("Home dashboard coming next — Day 23")


elif page == "👤 Company Profile":
    st.header("👤 Company Profile")
    st.info("Company Profile coming next — Day 23")


elif page == "🔎 Screener":
    st.header("🔎 Screener")
    st.info("Screener coming next — Day 24")


elif page == "👥 Peer Comparison":
    st.header("👥 Peer Comparison")
    st.info("Peer Comparison coming next — Day 24")


elif page == "📈 Trend Analysis":
    st.header("📈 Trend Analysis")
    st.info("Trend Analysis coming next — Day 25")


elif page == "🏢 Sector Analysis":
    st.header("🏢 Sector Analysis")
    st.info("Sector Analysis coming next — Day 25")


elif page == "💰 Capital Allocation":
    st.header("💰 Capital Allocation")
    st.info("Capital Allocation coming next — Day 25")


elif page == "📄 Annual Reports":
    st.header("📄 Annual Reports")
    st.info("Annual Reports coming next — Day 25")
