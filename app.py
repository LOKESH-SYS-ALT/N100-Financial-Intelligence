import streamlit as st
import requests
import pandas as pd


# ============================================================
# CONFIG
# ============================================================

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="N100 Financial Intelligence",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# API HELPERS
# ============================================================

def api_get(endpoint: str):
    response = requests.get(
        f"{API_BASE_URL}{endpoint}",
        timeout=15,
    )

    response.raise_for_status()

    return response.json()


def api_post(endpoint: str, payload: dict):
    response = requests.post(
        f"{API_BASE_URL}{endpoint}",
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# API HEALTH CHECK
# ============================================================

try:
    health = api_get("/health")

    if health.get("status") == "healthy":
        st.success("🟢 API Connected")
    else:
        st.error("API returned an unhealthy status")
        st.stop()

except requests.RequestException as error:
    st.error(
        "🔴 API is not running.\n\n"
        "Start FastAPI first:\n\n"
        "uvicorn api.main:app --reload"
    )
    st.stop()


# ============================================================
# LOAD COMPANIES
# ============================================================

try:
    companies_data = api_get("/companies")
    companies = companies_data.get("companies", [])

except requests.RequestException as error:
    st.error(f"Unable to load companies: {error}")
    st.stop()


companies_df = pd.DataFrame(companies)


# ============================================================
# HEADER
# ============================================================

st.title("📊 N100 Financial Intelligence")
st.caption(
    "Financial screening, quality scoring and company intelligence platform"
)


# ============================================================
# TOP METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "N100 Companies",
        companies_data.get("count", len(companies)),
    )

with col2:
    sectors = sorted(
        companies_df["broad_sector"]
        .dropna()
        .astype(str)
        .unique()
    )

    st.metric(
        "Sectors",
        len(sectors),
    )

with col3:
    total_market_cap = pd.to_numeric(
        companies_df.get("market_cap_cr"),
        errors="coerce",
    ).sum()

    st.metric(
        "Total Market Cap",
        f"₹{total_market_cap / 100000:.2f} L Cr",
    )

with col4:
    st.metric(
        "API Status",
        "Healthy",
    )


st.divider()


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🏠 Overview",
        "🔎 Screener",
        "🏢 Company Intelligence",
        "Peer Comparison"
    ]
)


# ============================================================
# OVERVIEW
# ============================================================

with tab1:

    st.subheader("📈 Market Overview")

    # --------------------------------------------------------
    # Get scored universe
    # --------------------------------------------------------

    try:
        overview_data = api_post(
            "/screener",
            {},
        )

        overview_results = overview_data.get(
            "results",
            [],
        )

        overview_df = pd.DataFrame(
            overview_results
        )

    except requests.RequestException:
        overview_df = pd.DataFrame()


    # --------------------------------------------------------
    # Top companies
    # --------------------------------------------------------

    if not overview_df.empty:

        st.subheader("🏆 Top Quality Companies")

        top_columns = [
            column
            for column in [
                "company_id",
                "company_name",
                "broad_sector",
                "market_cap_cr",
                "sales",
                "return_on_equity_pct",
                "debt_to_equity",
                "composite_quality_score",
            ]
            if column in overview_df.columns
        ]

        top_df = (
            overview_df[
                top_columns
            ]
            .sort_values(
                "composite_quality_score",
                ascending=False,
            )
            .head(10)
            .reset_index(drop=True)
        )

        st.dataframe(
            top_df,
            use_container_width=True,
            hide_index=True,
        )


        # ----------------------------------------------------
        # Sector distribution
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("🏭 Companies by Sector")

            sector_counts = (
                overview_df[
                    "broad_sector"
                ]
                .value_counts()
            )

            st.bar_chart(
                sector_counts
            )

        with col2:

            st.subheader(
                "⭐ Quality Score Distribution"
            )

            score_series = pd.to_numeric(
                overview_df[
                    "composite_quality_score"
                ],
                errors="coerce",
            )

            score_bins = pd.cut(
                score_series,
                bins=[
                    0,
                    20,
                    40,
                    60,
                    80,
                    100,
                ],
                labels=[
                    "0-20",
                    "21-40",
                    "41-60",
                    "61-80",
                    "81-100",
                ],
            )

            score_distribution = (
                score_bins
                .value_counts()
                .sort_index()
            )

            st.bar_chart(
                score_distribution
            )

    else:

        st.warning(
            "Unable to load quality scores."
        )


# ============================================================
# SCREENER
# ============================================================

with tab2:

    st.subheader("🔎 N100 Stock Screener")

    st.caption(
        "Apply financial filters and identify companies matching your criteria."
    )


    # --------------------------------------------------------
    # PRESETS
    # --------------------------------------------------------

    st.markdown("### 🎯 Preset Strategies")

    try:

        preset_data = api_get(
            "/presets"
        )

        preset_names = preset_data.get(
            "presets",
            [],
        )

    except requests.RequestException:

        preset_names = []


    preset_options = [
        "Custom Screener"
    ] + preset_names


    selected_preset = st.selectbox(
        "Select screening strategy",
        preset_options,
    )


    if selected_preset != "Custom Screener":

        if st.button(
            "🚀 Run Preset",
            use_container_width=True,
        ):

            try:

                result = api_get(
                    f"/presets/{selected_preset}"
                )

                preset_results = pd.DataFrame(
                    result.get(
                        "results",
                        [],
                    )
                )

                st.success(
                    f"Found {result.get('count', 0)} companies"
                )

                if not preset_results.empty:

                    st.dataframe(
                        preset_results,
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.markdown("### 📥 Export Results")

                    col1, col2 = st.columns(2)

                    with col1:

                        try:

                            from src.reports.exporter import export_excel

                            excel_path = export_excel(
                                preset_results,
                                f"{selected_preset}_screener",
                                sheet_name="Screener",
                            )

                            with open(
                                excel_path,
                                "rb",
                            ) as file:

                                st.download_button(
                                    label="📊 Download Excel",
                                    data=file,
                                    file_name=excel_path.name,
                                    mime=(
                                        "application/vnd.openxmlformats-officedocument."
                                        "spreadsheetml.sheet"
                                    ),
                                    key="download_screener_excel",
                                )

                        except Exception as error:

                            st.error(
                                f"Excel export failed: {error}"
                            )

                    with col2:

                        try:

                            from src.reports.exporter import export_pdf

                            pdf_path = export_pdf(
                                preset_results,
                                f"{selected_preset}_screener",
                                title=(
                                    f"N100 Financial Intelligence - "
                                    f"{selected_preset}"
                                ),
                            )

                            with open(
                                pdf_path,
                                "rb",
                            ) as file:

                                st.download_button(
                                    label="📄 Download PDF",
                                    data=file,
                                    file_name=pdf_path.name,
                                    mime="application/pdf",
                                    key="download_screener_pdf",
                                )

                        except Exception as error:

                            st.error(
                                f"PDF export failed: {error}"
                            )

            except requests.RequestException as error:

                st.error(
                    f"Preset request failed: {error}"
                )

    # --------------------------------------------------------
    # CUSTOM SCREENER
    # --------------------------------------------------------

    else:

        st.markdown("### ⚙️ Custom Filters")

        st.info(
            "Enable a filter only when you want to apply it."
        )


        # ----------------------------------------------------
        # PROFITABILITY
        # ----------------------------------------------------

        st.markdown("#### 💰 Profitability")

        col1, col2, col3 = st.columns(3)

        with col1:

            use_roe = st.checkbox(
                "Minimum ROE",
                value=False,
            )

            roe_min = st.number_input(
                "ROE (%)",
                min_value=-100.0,
                max_value=500.0,
                value=15.0,
                step=1.0,
                disabled=not use_roe,
            )

        with col2:

            use_opm = st.checkbox(
                "Minimum OPM",
                value=False,
            )

            opm_min = st.number_input(
                "OPM (%)",
                min_value=-100.0,
                max_value=200.0,
                value=15.0,
                step=1.0,
                disabled=not use_opm,
            )

        with col3:

            use_net_profit = st.checkbox(
                "Minimum Net Profit",
                value=False,
            )

            net_profit_min = st.number_input(
                "Net Profit",
                min_value=0.0,
                value=1000.0,
                step=100.0,
                disabled=not use_net_profit,
            )


        # ----------------------------------------------------
        # LEVERAGE
        # ----------------------------------------------------

        st.markdown("#### 🏦 Leverage")

        col1, col2 = st.columns(2)

        with col1:

            use_de = st.checkbox(
                "Maximum Debt / Equity",
                value=False,
            )

            de_max = st.number_input(
                "D/E",
                min_value=0.0,
                max_value=100.0,
                value=1.0,
                step=0.1,
                disabled=not use_de,
            )

        with col2:

            use_icr = st.checkbox(
                "Minimum Interest Coverage",
                value=False,
            )

            icr_min = st.number_input(
                "ICR",
                min_value=0.0,
                max_value=1000.0,
                value=3.0,
                step=0.5,
                disabled=not use_icr,
            )


        # ----------------------------------------------------
        # GROWTH
        # ----------------------------------------------------

        st.markdown("#### 🚀 Growth")

        col1, col2, col3 = st.columns(3)

        with col1:

            use_revenue_growth = st.checkbox(
                "Minimum Revenue CAGR",
                value=False,
            )

            revenue_growth_min = st.number_input(
                "Revenue CAGR 5Y (%)",
                min_value=-100.0,
                max_value=200.0,
                value=10.0,
                step=1.0,
                disabled=not use_revenue_growth,
            )

        with col2:

            use_pat_growth = st.checkbox(
                "Minimum PAT CAGR",
                value=False,
            )

            pat_growth_min = st.number_input(
                "PAT CAGR 5Y (%)",
                min_value=-100.0,
                max_value=200.0,
                value=10.0,
                step=1.0,
                disabled=not use_pat_growth,
            )

        with col3:

            use_eps_growth = st.checkbox(
                "Minimum EPS CAGR",
                value=False,
            )

            eps_growth_min = st.number_input(
                "EPS CAGR 5Y (%)",
                min_value=-100.0,
                max_value=200.0,
                value=10.0,
                step=1.0,
                disabled=not use_eps_growth,
            )


        # ----------------------------------------------------
        # CASH FLOW
        # ----------------------------------------------------

        st.markdown("#### 💵 Cash Flow")

        col1, col2 = st.columns(2)

        with col1:

            use_fcf = st.checkbox(
                "Minimum Free Cash Flow",
                value=False,
            )

            fcf_min = st.number_input(
                "FCF",
                min_value=0.0,
                value=500.0,
                step=100.0,
                disabled=not use_fcf,
            )

        with col2:

            use_sales = st.checkbox(
                "Minimum Sales",
                value=False,
            )

            sales_min = st.number_input(
                "Sales",
                min_value=0.0,
                value=5000.0,
                step=500.0,
                disabled=not use_sales,
            )


        # ----------------------------------------------------
        # VALUATION
        # ----------------------------------------------------

        st.markdown("#### 💎 Valuation")

        col1, col2, col3 = st.columns(3)

        with col1:

            use_pe = st.checkbox(
                "Maximum P/E",
                value=False,
            )

            pe_max = st.number_input(
                "P/E",
                min_value=0.0,
                value=40.0,
                step=1.0,
                disabled=not use_pe,
            )

        with col2:

            use_pb = st.checkbox(
                "Maximum P/B",
                value=False,
            )

            pb_max = st.number_input(
                "P/B",
                min_value=0.0,
                value=8.0,
                step=0.5,
                disabled=not use_pb,
            )

        with col3:

            use_dividend = st.checkbox(
                "Minimum Dividend Yield",
                value=False,
            )

            dividend_min = st.number_input(
                "Dividend Yield (%)",
                min_value=0.0,
                value=2.0,
                step=0.5,
                disabled=not use_dividend,
            )


        # ----------------------------------------------------
        # RUN SCREENER
        # ----------------------------------------------------

        st.divider()

        if st.button(
            "🔍 Run Custom Screener",
            type="primary",
            use_container_width=True,
        ):

            filters = {}


            if use_roe:
                filters["roe_min"] = roe_min

            if use_opm:
                filters["opm_min"] = opm_min

            if use_net_profit:
                filters["net_profit_min"] = net_profit_min

            if use_de:
                filters["debt_to_equity_max"] = de_max

            if use_icr:
                filters["icr_min"] = icr_min

            if use_revenue_growth:
                filters[
                    "revenue_cagr_5yr_min"
                ] = revenue_growth_min

            if use_pat_growth:
                filters[
                    "pat_cagr_5yr_min"
                ] = pat_growth_min

            if use_eps_growth:
                filters[
                    "eps_cagr_5yr_min"
                ] = eps_growth_min

            if use_fcf:
                filters["fcf_min"] = fcf_min

            if use_sales:
                filters["sales_min"] = sales_min

            if use_pe:
                filters["pe_max"] = pe_max

            if use_pb:
                filters["pb_max"] = pb_max

            if use_dividend:
                filters[
                    "dividend_yield_min"
                ] = dividend_min


            try:

                result = api_post(
                    "/screener",
                    filters,
                )

                results_df = pd.DataFrame(
                    result.get(
                        "results",
                        [],
                    )
                )


                st.success(
                    f"🎯 {result.get('count', 0)} companies matched"
                )


                if not results_df.empty:

                    st.dataframe(
                        results_df,
                        use_container_width=True,
                        hide_index=True,
                    )
                                        # ------------------------------------------------
                    # Export Custom Screener Results
                    # ------------------------------------------------

                    st.markdown("### 📥 Export Results")

                    export_col1, export_col2 = st.columns(2)

                    with export_col1:

                        try:

                            from src.reports.exporter import export_excel

                            excel_path = export_excel(
                                results_df,
                                "custom_screener_results",
                                sheet_name="Screener",
                            )

                            with open(excel_path, "rb") as file:

                                st.download_button(
                                    label="📊 Download Excel",
                                    data=file,
                                    file_name=excel_path.name,
                                    mime=(
                                        "application/vnd.openxmlformats-officedocument."
                                        "spreadsheetml.sheet"
                                    ),
                                    key="download_custom_screener_excel",
                                )

                        except Exception as error:

                            st.error(
                                f"Excel export failed: {error}"
                            )


                    with export_col2:

                        try:

                            from src.reports.exporter import export_pdf

                            pdf_path = export_pdf(
                                results_df,
                                "custom_screener_results",
                                title=(
                                    "N100 Financial Intelligence - "
                                    "Custom Screener"
                                ),
                            )

                            with open(pdf_path, "rb") as file:

                                st.download_button(
                                    label="📄 Download PDF",
                                    data=file,
                                    file_name=pdf_path.name,
                                    mime="application/pdf",
                                    key="download_custom_screener_pdf",
                                )

                        except Exception as error:

                            st.error(
                                f"PDF export failed: {error}"
                            )
                else:

                    st.warning(
                        "No companies matched these filters."
                    )


            except requests.RequestException as error:

                st.error(
                    f"Screener request failed: {error}"
                )


# ============================================================
# COMPANY INTELLIGENCE
# ============================================================

with tab3:

    st.subheader("🏢 Company Intelligence")

    st.caption(
        "Explore detailed financial metrics for an individual N100 company."
    )


    company_ids = sorted(
        companies_df[
            "company_id"
        ]
        .dropna()
        .astype(str)
        .tolist()
    )


    selected_company = st.selectbox(
        "Select Company",
        company_ids,
    )


    if st.button(
        "📊 Load Company Intelligence",
        use_container_width=True,
    ):

        try:

            company = api_get(
                f"/companies/{selected_company}"
            )

            st.success(
                f"Loaded {company.get('company_name', selected_company)}"
            )


            # ------------------------------------------------
            # Company Header
            # ------------------------------------------------

            st.markdown(
                f"## {company.get('company_name', selected_company)}"
            )

            st.caption(
                f"{company.get('company_id', '')} • "
                f"{company.get('broad_sector', 'N/A')}"
            )



            # ------------------------------------------------
            # Key Metrics
            # ------------------------------------------------

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Market Cap",
                    f"₹{company.get('market_cap_cr', 0):,.0f} Cr"
                    if isinstance(
                        company.get("market_cap_cr"),
                        (int, float),
                    )
                    else "N/A",
                )

            with col2:

                st.metric(
                    "ROE",
                    (
                        f"{company.get('return_on_equity_pct', 0):.2f}%"
                        if isinstance(
                            company.get(
                                "return_on_equity_pct"
                            ),
                            (int, float),
                        )
                        else "N/A"
                    ),
                )

            with col3:

                st.metric(
                    "Debt / Equity",
                    (
                        f"{company.get('debt_to_equity', 0):.2f}"
                        if isinstance(
                            company.get(
                                "debt_to_equity"
                            ),
                            (int, float),
                        )
                        else "N/A"
                    ),
                )

            with col4:

                st.metric(
                    "Quality Score",
                    (
                        f"{company.get('composite_quality_score', 0):.2f}"
                        if isinstance(
                            company.get(
                                "composite_quality_score"
                            ),
                            (int, float),
                        )
                        else "N/A"
                    ),
                )


            st.divider()


            # ------------------------------------------------
            # Financial Metrics
            # ------------------------------------------------

            st.subheader("📋 Financial Metrics")


            detail_fields = [
                "sales",
                "net_profit",
                "eps",
                "opm_percentage",
                "dividend_yield_pct",
                "price_to_earnings",
                "price_to_book",
                "free_cash_flow_cr",
                "cash_from_operations_cr",
                "return_on_capital_employed_pct",
                "return_on_assets_pct",
                "revenue_cagr_5yr",
                "pat_cagr_5yr",
                "eps_cagr_5yr",
                "interest_coverage",
                "total_debt_cr",
                "borrowings",
                "total_assets",
                "equity_capital",
                "reserves",
            ]


            detail_rows = []

            for field in detail_fields:

                if field in company:

                    detail_rows.append(
                        {
                            "Metric": field.replace(
                                "_",
                                " ",
                            ).title(),
                            "Value": company[field],
                        }
                    )


            # ------------------------------------------------
            # Export Company Report
            # ------------------------------------------------

            st.markdown("### 📥 Export Company Report")

            export_col1, export_col2 = st.columns(2)

            with export_col1:

                try:

                    from src.reports.exporter import export_excel

                    company_report_df = pd.DataFrame(
                        [
                            {
                                "Company ID": company.get(
                                    "company_id",
                                    selected_company,
                                ),
                                "Company Name": company.get(
                                    "company_name",
                                    "",
                                ),
                                "Sector": company.get(
                                    "broad_sector",
                                    "",
                                ),
                                "Market Cap (Cr)": company.get(
                                    "market_cap_cr"
                                ),
                                "ROE (%)": company.get(
                                    "return_on_equity_pct"
                                ),
                                "Debt / Equity": company.get(
                                    "debt_to_equity"
                                ),
                                "Quality Score": company.get(
                                    "composite_quality_score"
                                ),
                            }
                        ]
                    )

                    excel_path = export_excel(
                        company_report_df,
                        f"{selected_company}_company_report",
                        sheet_name="Company Report",
                    )

                    with open(excel_path, "rb") as file:

                        st.download_button(
                            label="📊 Download Excel",
                            data=file,
                            file_name=excel_path.name,
                            mime=(
                                "application/vnd.openxmlformats-officedocument."
                                "spreadsheetml.sheet"
                            ),
                            key="download_company_excel",
                        )

                except Exception as error:

                    st.error(
                        f"Excel export failed: {error}"
                    )


            with export_col2:

                try:

                    from src.reports.exporter import export_pdf

                    pdf_path = export_pdf(
                        company_report_df,
                        f"{selected_company}_company_report",
                        title=(
                            f"N100 Financial Intelligence - "
                            f"{company.get('company_name', selected_company)}"
                        ),
                    )

                    with open(pdf_path, "rb") as file:

                        st.download_button(
                            label="📄 Download PDF",
                            data=file,
                            file_name=pdf_path.name,
                            mime="application/pdf",
                            key="download_company_pdf",
                        )

                except Exception as error:

                    st.error(
                        f"PDF export failed: {error}"
                    )    


        except requests.HTTPError as error:

            st.error(
                f"Company not found: {selected_company}"
            )

        except requests.RequestException as error:

            st.error(
                f"Unable to load company: {error}"
            )


# ============================================================
# PEER COMPARISON
# ============================================================

with tab4:

    st.header("Peer Comparison")

    peer_company = st.selectbox(
    "Select Company",
    [c["company_id"] for c in companies],
    key="peer_company",
)

    if st.button(
        "Compare with Peers",
        key="compare_peers",
    ):

        try:

            response = requests.get(
                f"{API_BASE_URL}/companies/{peer_company}/peers",
                timeout=10,
            )

            if response.status_code == 200:

                data = response.json()

                st.success(
                    f"Peer Group: {data['peer_group_name']} | "
                    f"Companies: {data['peer_count']}"
                )

                peer_df = pd.DataFrame(
                    data["results"]
                )

                display_columns = [
                    "company_id",
                    "company_name",
                    "is_benchmark",
                    "selected_company",
                    "net_profit_margin_pct",
                    "operating_profit_margin_pct",
                    "interest_coverage",
                    "earnings_per_share",
                    "book_value_per_share",
                    "composite_quality_score",
                ]

                display_columns = [
                    column
                    for column in display_columns
                    if column in peer_df.columns
                ]

                st.dataframe(
                    peer_df[display_columns],
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.error(
                    f"Peer comparison failed: {response.text}"
                )

        except requests.RequestException as error:

            st.error(
                f"Unable to load peer comparison: {error}"
            )




# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "N100 Financial Intelligence • "
    "Analytics platform • v1.0"
)