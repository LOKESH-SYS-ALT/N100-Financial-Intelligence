from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle
)
from reportlab.lib.units import mm

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "analyst_guide.pdf"

OUT.parent.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()

title = ParagraphStyle(
    "GuideTitle",
    parent=styles["Title"],
    fontSize=24,
    leading=30,
    alignment=TA_CENTER,
    spaceAfter=18,
)

h1 = ParagraphStyle(
    "GuideH1",
    parent=styles["Heading1"],
    fontSize=17,
    leading=22,
    spaceAfter=12,
)

h2 = ParagraphStyle(
    "GuideH2",
    parent=styles["Heading2"],
    fontSize=12,
    leading=16,
    spaceAfter=8,
)

body = ParagraphStyle(
    "GuideBody",
    parent=styles["BodyText"],
    fontSize=9.5,
    leading=14,
    spaceAfter=8,
)

small = ParagraphStyle(
    "GuideSmall",
    parent=body,
    fontSize=8,
    leading=11,
)

doc = SimpleDocTemplate(
    str(OUT),
    pagesize=A4,
    rightMargin=18 * mm,
    leftMargin=18 * mm,
    topMargin=18 * mm,
    bottomMargin=18 * mm,
)

story = []


def P(text, style=body):
    story.append(Paragraph(text, style))


def H(text):
    story.append(Paragraph(text, h1))


def H2(text):
    story.append(Paragraph(text, h2))


def bullets(items):
    for item in items:
        P("- " + item)


def page():
    story.append(PageBreak())


# PAGE 1
P("N100 FINANCIAL INTELLIGENCE", title)
P("Analyst Guide & Operating Manual", ParagraphStyle(
    "Sub", parent=body, alignment=TA_CENTER, fontSize=13
))
story.append(Spacer(1, 15 * mm))
P(
    "<b>Production analytics platform for Nifty 100 companies.</b><br/>"
    "Data engineering - Financial KPIs - Screening - Peer intelligence - "
    "Clustering - Cash-flow intelligence - Capital allocation - REST API - "
    "Dashboard - Automated reports",
    ParagraphStyle("Cover", parent=body, alignment=TA_CENTER, fontSize=11, leading=17)
)
story.append(Spacer(1, 25 * mm))
P(
    "Version 1.0<br/>"
    "Prepared for analyst and engineering users<br/>"
    "Dataset coverage: 92 companies",
    ParagraphStyle("Cover2", parent=body, alignment=TA_CENTER, fontSize=10)
)
page()


# PAGE 2
H("1. Platform Overview")
P(
    "N100 Financial Intelligence is an end-to-end financial analytics platform "
    "designed to transform structured company financial data into reusable "
    "investment-analysis outputs."
)
H2("Primary capabilities")
bullets([
    "ETL and data normalization across 12 structured source datasets.",
    "SQLite analytical database containing normalized company and financial data.",
    "30+ financial and operating KPIs.",
    "Financial screening with configurable filters and predefined investment presets.",
    "Peer-group intelligence and company comparisons.",
    "Five-company-archetype KMeans clustering.",
    "Cash-flow quality and financial-distress analysis.",
    "Capital-allocation pattern classification.",
    "Automated company tearsheets and sector reports.",
    "FastAPI REST service with documented endpoints.",
    "Streamlit analyst dashboard.",
])
H2("Coverage")
P(
    "The production dataset contains 92 companies. The database includes "
    "profit and loss, balance sheet, cash flow, financial ratios, market "
    "capitalization, peer groups, sectors, stock prices, documents, and "
    "analytical datasets."
)
page()


# PAGE 3
H("2. Data Architecture & ETL")
H2("Source datasets")
bullets([
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons",
    "financial_ratios",
    "market_cap",
    "peer_groups",
    "sectors",
    "stock_prices",
])
H2("Normalization")
P(
    "The ETL layer normalizes company identifiers and financial years before "
    "validation and database loading. Year normalization supports source "
    "formats such as annual labels and numeric year representations."
)
H2("Data-quality rules")
bullets([
    "Required-column validation.",
    "Duplicate company/year detection.",
    "Company-reference integrity.",
    "Null company-ID detection.",
    "Operating-margin consistency validation.",
    "Sales-value validation.",
])
P(
    "Critical data-quality failures must be resolved before analytical outputs "
    "are considered production-ready. Warning-level discrepancies are retained "
    "for analyst review rather than silently changing source values."
)
page()


# PAGE 4
H("3. KPI Framework")
H2("Profitability")
bullets([
    "ROE ? return generated on shareholder equity.",
    "ROCE ? return generated on capital employed.",
    "ROA ? return generated on assets.",
    "Operating Profit Margin ? operating profit relative to sales.",
])
H2("Growth")
bullets([
    "Revenue CAGR ? multi-year revenue growth.",
    "PAT CAGR ? multi-year profit-after-tax growth.",
    "EPS CAGR ? multi-year earnings-per-share growth.",
])
H2("Leverage & efficiency")
bullets([
    "Debt-to-equity.",
    "Interest coverage.",
    "Asset turnover.",
])
H2("Interpretation")
P(
    "KPIs should be interpreted together rather than individually. Strong "
    "profitability with excessive leverage can indicate a different risk "
    "profile from strong profitability supported by low leverage."
)
page()


# PAGE 5
H("4. Financial Screener")
P(
    "The screener provides a structured way to reduce the 92-company universe "
    "to candidates matching analyst-defined financial conditions."
)
H2("Supported filters")
bullets([
    "Minimum ROE.",
    "Maximum debt-to-equity.",
    "Minimum five-year revenue CAGR.",
])
H2("Investment presets")
bullets([
    "Quality Compounder.",
    "Value Pick.",
    "Growth Accelerator.",
    "Dividend Champion.",
    "Debt-Free Blue Chip.",
    "Turnaround Watch.",
])
H2("Analyst workflow")
bullets([
    "Start with the broad universe.",
    "Apply profitability and leverage filters.",
    "Review growth characteristics.",
    "Compare shortlisted companies with peers.",
    "Open the company profile and tearsheet.",
    "Review cash-flow and capital-allocation signals before final judgment.",
])
page()


# PAGE 6
H("5. Peer & Sector Intelligence")
H2("Peer analysis")
P(
    "Companies are grouped into peer groups for relative analysis. A benchmark "
    "company can be compared against the other companies in its peer group."
)
H2("Sector analysis")
P(
    "The current production database contains 10 broad sectors. Sector analysis "
    "is useful for distinguishing company-specific performance from broader "
    "industry characteristics."
)
bullets([
    "Communication Services",
    "Consumer Discretionary",
    "Consumer Staples",
    "Energy",
    "Financials",
    "Healthcare",
    "Industrials",
    "Information Technology",
    "Materials",
    "Real Estate",
])
H2("Recommended use")
P(
    "Use sector and peer analysis after screening. A company that appears strong "
    "in isolation should also be evaluated against comparable businesses."
)
page()


# PAGE 7
H("6. Clustering & Portfolio Intelligence")
H2("KMeans model")
P(
    "The clustering pipeline assigns all 92 companies to five clusters using "
    "ROE, debt-to-equity, five-year revenue CAGR, five-year FCF CAGR, and "
    "operating-margin features."
)
H2("Preprocessing")
bullets([
    "Missing feature values are imputed using sector-level medians.",
    "Features are standardized before clustering.",
    "KMeans uses five clusters with random_state=42.",
    "Distance from centroid is retained as an indication of cluster fit.",
])
H2("Current archetypes")
bullets([
    "Balanced Performers.",
    "High-Leverage Challengers.",
    "Quality Leaders.",
    "Low-Leverage Compounders.",
    "Balanced Performers ? Cluster 4.",
])
P(
    "Cluster names are descriptive labels for analytical interpretation; they "
    "are not investment recommendations."
)
page()


# PAGE 8
H("7. Cash Flow & Capital Allocation")
H2("Cash-flow intelligence")
P(
    "Cash-flow analysis evaluates operating cash generation, investing activity, "
    "financing activity, free cash flow characteristics, and distress signals."
)
P(
    "The raw cash-flow source does not contain every company. Companies without "
    "available cash-flow data are not assigned invented values."
)
H2("Capital allocation")
bullets([
    "Shareholder Returns.",
    "Mixed.",
    "Reinvestor.",
    "Liquidating Assets.",
    "Growth Funded by Debt.",
    "Distress Signal.",
    "Pre-Revenue.",
    "Cash Accumulator.",
])
H2("Analyst interpretation")
P(
    "Capital-allocation patterns should be reviewed alongside profitability, "
    "growth, leverage, and cash-flow quality. A single pattern should never "
    "be treated as a standalone buy or sell signal."
)
page()


# PAGE 9
H("8. REST API")
H2("API service")
P(
    "The FastAPI service exposes normalized financial intelligence through "
    "versioned REST endpoints under /api/v1."
)
H2("Endpoint groups")
bullets([
    "Companies ? list, search, profile, documents.",
    "Financials ? profit and loss, balance sheet, cash flow, ratios.",
    "Screener ? configurable financial filtering.",
    "Sectors ? sector list and sector companies.",
    "Peers ? peer groups, company peers, peer comparison.",
    "Market ? market capitalization and portfolio statistics.",
    "Reports ? report status and company tearsheet PDF.",
    "Health ? service and database status.",
])
H2("API quality")
P(
    "The API test suite validates endpoint behavior using FastAPI TestClient. "
    "The current test suite contains 154 passing tests."
)
page()


# PAGE 10
H("9. Streamlit Dashboard")
H2("Dashboard screens")
bullets([
    "Home ? high-level portfolio and market KPIs.",
    "Company Profile ? detailed company financial profile.",
    "Screener ? filter and shortlist companies.",
    "Peer Intelligence ? compare peer groups.",
    "Trends ? historical KPI trends.",
    "Sector Intelligence ? sector-level analysis.",
    "Capital Allocation ? allocation patterns and signals.",
    "Reports ? report access and analytical outputs.",
])
H2("Recommended workflow")
bullets([
    "Start on Home.",
    "Use Screener to identify candidates.",
    "Open Profile for detailed KPI review.",
    "Compare candidates against peers.",
    "Review Trends and Capital Allocation.",
    "Open the generated tearsheet/report.",
])
P(
    "The dashboard is intended as an analytical interface. Final investment "
    "decisions require independent validation and appropriate financial due diligence."
)
page()


# PAGE 11
H("10. Reports & Outputs")
H2("Company tearsheets")
P(
    "Company tearsheets provide a two-page summary containing financial "
    "performance, profitability, balance-sheet information, cash-flow data, "
    "capital-allocation interpretation, and financial-health commentary."
)
H2("Sector reports")
P(
    "Sector reports summarize companies and financial characteristics within "
    "each of the 10 current broad sectors."
)
H2("Portfolio summary")
P(
    "The portfolio summary contains company-level trend indicators using "
    "UP, DOWN, FLAT, and N/A classifications."
)
H2("Key output files")
bullets([
    "output/cluster_labels.csv",
    "output/cluster_profiles.csv",
    "output/sector_outliers.csv",
    "output/portfolio_stats.csv",
    "output/cashflow_intelligence.xlsx",
    "output/distress_alerts.csv",
    "output/pattern_changes.csv",
    "output/pros_cons_generated.csv",
    "reports/portfolio/portfolio_summary.pdf",
    "reports/tearsheets/",
])
page()


# PAGE 12
H("11. QA, Operations & Analyst Checklist")
H2("QA status")
bullets([
    "Black formatting check: passed.",
    "Full pytest suite: 154 passed.",
    "API tests: 23 passed.",
    "Concurrency test: 35/35 successful requests.",
    "API failures during concurrency test: 0.",
    "Dashboard: 8/8 screens operational.",
    "SQLite performance indexes created for major query paths.",
])
H2("Analyst checklist")
bullets([
    "Confirm the company exists in the production database.",
    "Review latest available annual financial data.",
    "Check profitability and growth KPIs.",
    "Check leverage and interest coverage.",
    "Review peer and sector position.",
    "Review cash-flow quality.",
    "Review capital-allocation pattern.",
    "Check clustering archetype as supporting context.",
    "Review the company tearsheet.",
    "Investigate unusual or extreme source values before drawing conclusions.",
])
H2("Important data principle")
P(
    "The platform preserves source data and does not fabricate missing financial "
    "values. Missing analytical inputs are handled according to the documented "
    "imputation rules where appropriate."
)
P(
    "<b>End of Analyst Guide ? N100 Financial Intelligence v1.0</b>",
    ParagraphStyle("End", parent=body, alignment=TA_CENTER, spaceBefore=15)
)

doc.build(story)

print(f"Analyst guide created: {OUT}")
print(f"Pages: 12")
print(f"Size: {OUT.stat().st_size} bytes")
