"""
N100 Financial Intelligence
Sprint 5 - Company Tearsheet PDF

Day 33:
- 2-page company tearsheet
- KPI tiles
- Revenue / Net Profit charts
- ROE / ROCE trend
- Balance Sheet
- Cash Flow
- Pros / Cons
- Capital Allocation
"""

from pathlib import Path
import sqlite3

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import LineChart
from reportlab.graphics.charts.lineplots import LinePlot

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "tearsheets"


# -------------------------------------------------------------------
# Database
# -------------------------------------------------------------------


def get_connection():
    return sqlite3.connect(DB_PATH)


def load_company_data(company_id: str):
    conn = get_connection()

    company = pd.read_sql(
        """
        SELECT *
        FROM companies
        WHERE id = ?
        """,
        conn,
        params=[company_id],
    )

    ratios = pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[company_id],
    )

    pnl = pd.read_sql(
        """
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[company_id],
    )

    balance = pd.read_sql(
        """
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[company_id],
    )

    cashflow = pd.read_sql(
        """
        SELECT *
        FROM cashflow
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[company_id],
    )

    sectors = pd.read_sql(
        """
        SELECT *
        FROM sectors
        WHERE company_id = ?
        """,
        conn,
        params=[company_id],
    )

    peers = pd.read_sql(
        """
        SELECT *
        FROM peer_groups
        WHERE company_id = ?
        """,
        conn,
        params=[company_id],
    )

    conn.close()

    return {
        "company": company,
        "ratios": ratios,
        "pnl": pnl,
        "balance": balance,
        "cashflow": cashflow,
        "sectors": sectors,
        "peers": peers,
    }


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------


def safe_number(value, decimals=2):
    try:
        if pd.isna(value):
            return "N/A"
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "N/A"


def find_column(df, candidates):
    for column in candidates:
        if column in df.columns:
            return column


def latest_row(df):
    if df.empty:
        return None

    df = df.copy()
    df["year_text"] = df["year"].astype(str).str.strip()

    # Prefer latest annual March row with actual KPI data.
    march_rows = df[df["year_text"].str.lower().str.startswith("mar")].copy()

    if not march_rows.empty:
        march_rows["year_num"] = pd.to_numeric(
            march_rows["year_text"].str.extract(r"(\d{4})")[0],
            errors="coerce",
        )
        march_rows = march_rows.sort_values("year_num")

        kpi_cols = [
            "return_on_equity_pct",
            "return_on_capital_employed_pct",
            "debt_to_equity",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "eps_cagr_5yr",
        ]

        available = [c for c in kpi_cols if c in march_rows.columns]

        if available:
            valid = march_rows.dropna(subset=available, how="all")
            if not valid.empty:
                return valid.iloc[-1].drop(
                    labels=["year_text", "year_num"], errors="ignore"
                )

        return march_rows.iloc[-1].drop(
            labels=["year_text", "year_num"], errors="ignore"
        )

    return df.iloc[-1].drop(labels=["year_text"], errors="ignore")

    return None


def get_company_name(data):
    company = data["company"]

    if company.empty:
        return "Unknown Company"

    return str(
        company.iloc[0].get(
            "company_name",
            company.iloc[0].get("id", "Unknown Company"),
        )
    )


def get_sector(data):
    sectors = data["sectors"]

    if not sectors.empty:
        return str(
            sectors.iloc[0].get(
                "broad_sector",
                "Unknown",
            )
        )

    return "Unknown"


# -------------------------------------------------------------------
# Styles
# -------------------------------------------------------------------

styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "TearsheetTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=20,
    leading=24,
    textColor=colors.white,
    alignment=TA_LEFT,
)

SUBTITLE_STYLE = ParagraphStyle(
    "TearsheetSubtitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=colors.white,
)

SECTION_STYLE = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=15,
    textColor=colors.HexColor("#17365D"),
    spaceBefore=5,
    spaceAfter=5,
)

BODY_STYLE = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=11,
)

SMALL_STYLE = ParagraphStyle(
    "Small",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=7,
    leading=9,
)

SIGNAL_STYLE = ParagraphStyle(
    "Signal",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=8,
    leading=10,
)


# -------------------------------------------------------------------
# Header
# -------------------------------------------------------------------


def header_block(company_name, ticker, sector):
    data = [
        [
            Paragraph(
                f"N100 FINANCIAL INTELLIGENCE<br/>{company_name}",
                TITLE_STYLE,
            ),
            Paragraph(
                f"<b>{ticker}</b><br/>{sector}",
                SUBTITLE_STYLE,
            ),
        ]
    ]

    table = Table(
        data,
        colWidths=[125 * mm, 50 * mm],
        rowHeights=[24 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#17365D"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    return table


# -------------------------------------------------------------------
# KPI tiles
# -------------------------------------------------------------------


def kpi_tiles(ratios):
    latest = latest_row(ratios)

    if latest is None:
        return Paragraph("No ratio data available.", BODY_STYLE)

    def value(column, suffix=""):
        if column not in latest.index:
            return "N/A"

        number = pd.to_numeric(
            pd.Series([latest.get(column)]),
            errors="coerce",
        ).iloc[0]

        if pd.isna(number):
            return "N/A"

        return f"{number:,.2f}{suffix}"

    kpis = [
        ("ROE", value("return_on_equity_pct", "%")),
        ("ROCE", value("return_on_capital_employed_pct", "%")),
        ("D/E", value("debt_to_equity")),
        ("Revenue CAGR", value("revenue_cagr_5yr", "%")),
        ("PAT CAGR", value("pat_cagr_5yr", "%")),
        ("EPS CAGR", value("eps_cagr_5yr", "%")),
    ]

    cells = []

    for label, display_value in kpis:
        cell = Table(
            [
                [Paragraph(label, SMALL_STYLE)],
                [
                    Paragraph(
                        f"<b>{display_value}</b>",
                        ParagraphStyle(
                            "KPIValue",
                            parent=BODY_STYLE,
                            fontSize=12,
                            leading=15,
                            textColor=colors.HexColor("#17365D"),
                        ),
                    )
                ],
            ],
            colWidths=[28 * mm],
            rowHeights=[7 * mm, 10 * mm],
        )

        cell.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F7FA")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        cells.append(cell)

    outer = Table(
        [cells],
        colWidths=[29 * mm] * 6,
        hAlign="LEFT",
    )

    outer.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B7C9D6")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    return outer


# -------------------------------------------------------------------
# Charts
# -------------------------------------------------------------------
def revenue_profit_chart(pnl):
    if pnl.empty:
        return Paragraph(
            "No profit and loss data available.",
            BODY_STYLE,
        )

    temp = pnl.copy()

    year_col = find_column(
        temp,
        ["year", "Year"],
    )

    if not year_col:
        return Paragraph(
            "Profit and loss year unavailable.",
            BODY_STYLE,
        )

    revenue_col = find_column(
        temp,
        [
            "revenue",
            "sales",
            "Revenue",
            "Sales",
        ],
    )

    profit_col = find_column(
        temp,
        [
            "net_profit",
            "net profit",
            "Net Profit",
            "profit_after_tax",
            "pat",
        ],
    )

    if not revenue_col or not profit_col:
        return Paragraph(
            "Revenue / Net Profit data unavailable.",
            BODY_STYLE,
        )

    temp[revenue_col] = pd.to_numeric(
        temp[revenue_col],
        errors="coerce",
    )

    temp[profit_col] = pd.to_numeric(
        temp[profit_col],
        errors="coerce",
    )

    temp["year_text"] = temp[year_col].astype(str).str.strip()

    # Prefer March annual periods.
    march = temp[temp["year_text"].str.lower().str.startswith("mar")].copy()

    if not march.empty:
        march["year_num"] = pd.to_numeric(
            march["year_text"].str.extract(r"(20\d{2}|19\d{2})")[0],
            errors="coerce",
        )

        march = march.sort_values("year_num").drop_duplicates(
            subset=["year_num"],
            keep="last",
        )

        temp = march.tail(10).copy()

    else:
        temp = temp.tail(10).copy()

    if temp.empty:
        return Paragraph(
            "Revenue / Net Profit data unavailable.",
            BODY_STYLE,
        )

    labels = temp["year_text"].tolist()

    revenue_values = [
        float(value) if pd.notna(value) else 0 for value in temp[revenue_col]
    ]

    profit_values = [
        float(value) if pd.notna(value) else 0 for value in temp[profit_col]
    ]

    # Two separate charts, same 10-year period.
    revenue_chart = VerticalBarChart()

    revenue_chart.x = 0
    revenue_chart.y = 0
    revenue_chart.width = 112 * mm
    revenue_chart.height = 48 * mm

    revenue_chart.data = [revenue_values]

    revenue_chart.categoryAxis.categoryNames = labels
    revenue_chart.categoryAxis.labels.fontSize = 5
    revenue_chart.categoryAxis.labels.angle = 45
    revenue_chart.valueAxis.labels.fontSize = 5

    revenue_chart.barWidth = 8
    revenue_chart.groupSpacing = 8

    revenue_chart.strokeColor = None

    profit_chart = VerticalBarChart()

    profit_chart.x = 0
    profit_chart.y = 0
    profit_chart.width = 112 * mm
    profit_chart.height = 48 * mm

    profit_chart.data = [profit_values]

    profit_chart.categoryAxis.categoryNames = labels
    profit_chart.categoryAxis.labels.fontSize = 5
    profit_chart.categoryAxis.labels.angle = 45
    profit_chart.valueAxis.labels.fontSize = 5

    profit_chart.barWidth = 8
    profit_chart.groupSpacing = 8

    profit_chart.strokeColor = None

    drawing = Drawing(
        250 * mm,
        55 * mm,
    )

    revenue_chart.x = 0
    revenue_chart.y = 0

    profit_chart.x = 125 * mm
    profit_chart.y = 0

    drawing.add(revenue_chart)
    drawing.add(profit_chart)

    return drawing


def roe_roce_chart(ratios):
    if ratios.empty:
        return Paragraph(
            "ROE/ROCE data unavailable.",
            BODY_STYLE,
        )

    temp = ratios.copy()

    temp["year_text"] = temp["year"].astype(str).str.strip()

    temp = temp[temp["year_text"].str.lower().str.startswith("mar")].copy()

    if temp.empty:
        return Paragraph(
            "ROE/ROCE data unavailable.",
            BODY_STYLE,
        )

    temp["year_num"] = pd.to_numeric(
        temp["year_text"].str.extract(r"(20\d{2}|19\d{2})")[0],
        errors="coerce",
    )

    temp["roe"] = pd.to_numeric(
        temp["return_on_equity_pct"],
        errors="coerce",
    )

    temp["roce"] = pd.to_numeric(
        temp["return_on_capital_employed_pct"],
        errors="coerce",
    )

    temp = temp.dropna(
        subset=["year_num", "roe", "roce"],
    )

    if temp.empty:
        return Paragraph(
            "ROE/ROCE data unavailable.",
            BODY_STYLE,
        )

    temp = (
        temp.sort_values("year_num")
        .drop_duplicates(
            subset=["year_num"],
            keep="last",
        )
        .tail(10)
    )

    drawing = Drawing(
        250 * mm,
        55 * mm,
    )

    chart = LinePlot()

    chart.x = 15 * mm
    chart.y = 8 * mm
    chart.width = 215 * mm
    chart.height = 38 * mm

    roe = [
        (
            float(row["year_num"]),
            float(row["roe"]),
        )
        for _, row in temp.iterrows()
    ]

    roce = [
        (
            float(row["year_num"]),
            float(row["roce"]),
        )
        for _, row in temp.iterrows()
    ]

    chart.data = [
        roe,
        roce,
    ]

    chart.xValueAxis.valueMin = min(x for x, _ in roe)

    chart.xValueAxis.valueMax = max(x for x, _ in roe)

    chart.xValueAxis.labels.fontSize = 5
    chart.yValueAxis.labels.fontSize = 5
    chart.yValueAxis.valueMin = 0

    chart.lines[0].strokeWidth = 1.2
    chart.lines[1].strokeWidth = 1.2

    drawing.add(
        String(
            18 * mm,
            51 * mm,
            "ROE / ROCE - 10 Year Trend",
            fontSize=8,
            fontName="Helvetica-Bold",
        )
    )

    drawing.add(chart)

    return drawing


def balance_sheet_table(balance):
    drawing = Drawing(250 * mm, 58 * mm)

    if balance.empty:
        return Paragraph(
            "No balance sheet data available.",
            BODY_STYLE,
        )

    year_col = find_column(balance, ["year", "Year"])

    if not year_col:
        return Paragraph(
            "Balance sheet year unavailable.",
            BODY_STYLE,
        )

    asset_columns = [
        "fixed_assets",
        "cwip",
        "investments",
        "other_asset",
    ]

    available = [column for column in asset_columns if column in balance.columns]

    if not available:
        return Paragraph(
            "Balance sheet asset data unavailable.",
            BODY_STYLE,
        )

    temp = balance.copy()

    for column in available:
        temp[column] = pd.to_numeric(
            temp[column],
            errors="coerce",
        )

    temp["year_text"] = temp[year_col].astype(str).str.strip()

    march = temp[temp["year_text"].str.lower().str.startswith("mar")].copy()

    if not march.empty:
        march["year_num"] = pd.to_numeric(
            march["year_text"].str.extract(r"(\d{4})")[0],
            errors="coerce",
        )

        march = march.sort_values("year_num").drop_duplicates(
            subset=["year_num"],
            keep="last",
        )

        temp = march.tail(5).copy()
    else:
        temp = temp.tail(5).copy()

    chart = VerticalBarChart()

    chart.x = 15 * mm
    chart.y = 12 * mm
    chart.width = 225 * mm
    chart.height = 36 * mm

    chart.data = [temp[column].fillna(0).tolist() for column in available]

    chart.categoryAxis.categoryNames = temp["year_text"].tolist()

    chart.categoryAxis.labels.fontSize = 6
    chart.categoryAxis.labels.angle = 45
    chart.valueAxis.labels.fontSize = 6

    maximum = max(temp[available].sum(axis=1).tolist())

    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = maximum * 1.15 if maximum > 0 else 1
    chart.valueAxis.valueStep = chart.valueAxis.valueMax / 5

    chart.barWidth = 12
    chart.groupSpacing = 8

    drawing.add(chart)

    drawing.add(
        String(
            18 * mm,
            53 * mm,
            "Balance Sheet - Asset Composition",
            fontSize=8,
            fontName="Helvetica-Bold",
        )
    )

    return drawing


def cash_flow_table(cashflow):
    if cashflow.empty:
        return Paragraph(
            "No cash flow data available.",
            BODY_STYLE,
        )

    temp = cashflow.copy()

    year_col = find_column(
        temp,
        ["year", "Year"],
    )

    required = [
        "operating_activity",
        "investing_activity",
        "financing_activity",
    ]

    if not year_col:
        return Paragraph(
            "Cash flow year unavailable.",
            BODY_STYLE,
        )

    available = [column for column in required if column in temp.columns]

    if not available:
        return Paragraph(
            "Cash flow metrics unavailable.",
            BODY_STYLE,
        )

    for column in available:
        temp[column] = pd.to_numeric(
            temp[column],
            errors="coerce",
        )

    temp = temp.dropna(
        subset=available,
        how="all",
    )

    if temp.empty:
        return Paragraph(
            "Cash flow metrics unavailable.",
            BODY_STYLE,
        )

    temp["year_text"] = temp[year_col].astype(str).str.strip()

    march = temp[temp["year_text"].str.lower().str.startswith("mar")].copy()

    if not march.empty:
        march["year_num"] = pd.to_numeric(
            march["year_text"].str.extract(r"(\d{2,4})")[0],
            errors="coerce",
        )

        march = march.sort_values("year_num").drop_duplicates(
            subset=["year_num"],
            keep="last",
        )

        temp = march.tail(5).copy()
    else:
        temp = temp.tail(5).copy()

    drawing = Drawing(
        250 * mm,
        58 * mm,
    )

    drawing.add(
        String(
            18 * mm,
            53 * mm,
            "Cash Flow - 5 Year Trend",
            fontSize=8,
            fontName="Helvetica-Bold",
        )
    )

    drawing.add(
        String(
            18 * mm,
            48 * mm,
            "Operating, investing and financing cash flow",
            fontSize=6,
        )
    )

    values = []

    for _, row in temp.iterrows():
        cfo = (
            float(row["operating_activity"])
            if "operating_activity" in row and pd.notna(row["operating_activity"])
            else 0
        )

        cfi = (
            float(row["investing_activity"])
            if "investing_activity" in row and pd.notna(row["investing_activity"])
            else 0
        )

        cff = (
            float(row["financing_activity"])
            if "financing_activity" in row and pd.notna(row["financing_activity"])
            else 0
        )

        values.append(
            (
                cfo,
                cfi,
                cff,
            )
        )

    maximum = max(max(abs(value) for value in row) for row in values)

    chart_left = 20 * mm
    chart_bottom = 17 * mm
    chart_height = 25 * mm
    chart_width = 215 * mm

    if maximum > 0:
        scale = chart_height / maximum
    else:
        scale = 1

    zero_y = chart_bottom + chart_height / 2

    drawing.add(
        Line(
            chart_left,
            zero_y,
            chart_left + chart_width,
            zero_y,
        )
    )

    group_width = chart_width / max(
        len(values),
        1,
    )

    bar_width = 7 * mm
    bar_gap = 2 * mm

    labels = [
        "CFO",
        "CFI",
        "CFF",
    ]

    for index, row in enumerate(values):
        group_x = chart_left + index * group_width

        for component_index, value in enumerate(row):
            x = group_x + 4 * mm + component_index * (bar_width + bar_gap)

            height = abs(value) * scale

            if value >= 0:
                y = zero_y
            else:
                y = zero_y - height

            rect = Rect(
                x,
                y,
                bar_width,
                max(height, 0.7 * mm),
            )

            rect.strokeWidth = 0.3
            drawing.add(rect)

            value_text = (
                f"{value / 1000:.1f}k" if abs(value) >= 1000 else f"{value:.0f}"
            )

            drawing.add(
                String(
                    x + bar_width / 2,
                    y + height + 1.2 * mm if value >= 0 else y - 3 * mm,
                    value_text,
                    fontSize=5,
                    textAnchor="middle",
                )
            )

        year_label = String(
            group_x + 4 * mm + 1.5 * (bar_width + bar_gap),
            chart_bottom - 4 * mm,
            str(temp.iloc[index]["year_text"]),
            fontSize=6,
            textAnchor="middle",
        )

        drawing.add(year_label)

    legend_y = 8 * mm

    for index, label in enumerate(labels):
        legend_x = 85 * mm + index * 28 * mm

        drawing.add(
            Rect(
                legend_x,
                legend_y,
                4 * mm,
                2.5 * mm,
            )
        )

        drawing.add(
            String(
                legend_x + 6 * mm,
                legend_y,
                label,
                fontSize=6,
            )
        )

    return drawing


def pros_cons_table(company_id):
    file_path = PROJECT_ROOT / "output" / "pros_cons_generated.csv"

    if not file_path.exists():
        return Paragraph(
            "Generated Pros / Cons file not found.",
            BODY_STYLE,
        )

    try:
        pros_cons = pd.read_csv(file_path)

        pros_cons = pros_cons[
            pros_cons["company_id"].astype(str) == str(company_id)
        ].copy()

    except Exception as exc:
        return Paragraph(
            f"Pros / Cons unavailable: {exc}",
            BODY_STYLE,
        )

    if pros_cons.empty:
        return Paragraph(
            "No generated Pros / Cons available.",
            BODY_STYLE,
        )

    pros = (
        pros_cons[pros_cons["type"].astype(str).str.lower() == "pro"]
        .sort_values(
            "confidence_pct",
            ascending=False,
        )
        .head(6)
    )

    cons = (
        pros_cons[pros_cons["type"].astype(str).str.lower() == "con"]
        .sort_values(
            "confidence_pct",
            ascending=False,
        )
        .head(6)
    )

    max_rows = max(len(pros), len(cons))

    rows = [
        [
            Paragraph("<b>Pros</b>", BODY_STYLE),
            Paragraph("<b>Cons</b>", BODY_STYLE),
        ]
    ]

    for i in range(max_rows):
        pro_text = ""
        con_text = ""

        if i < len(pros):
            pro_text = str(pros.iloc[i]["text"])

        if i < len(cons):
            con_text = str(cons.iloc[i]["text"])

        rows.append(
            [
                Paragraph(
                    f"• {pro_text}" if pro_text else "",
                    SMALL_STYLE,
                ),
                Paragraph(
                    f"• {con_text}" if con_text else "",
                    SMALL_STYLE,
                ),
            ]
        )

    table = Table(
        rows,
        colWidths=[87 * mm, 87 * mm],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#E2F0D9")),
                ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FCE4D6")),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#B7B7B7")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    return table


# -------------------------------------------------------------------
# Capital allocation
# -------------------------------------------------------------------


def capital_allocation_badge(company_id):
    file_path = PROJECT_ROOT / "output" / "capital_allocation.csv"

    if not file_path.exists():
        return Paragraph(
            "Capital allocation data unavailable.",
            BODY_STYLE,
        )

    df = pd.read_csv(file_path)

    df = df[df["company_id"].astype(str) == str(company_id)].copy()

    if df.empty:
        return Paragraph(
            "Capital allocation data unavailable.",
            BODY_STYLE,
        )

    df = df[df["year"].astype(str).str.upper() != "TTM"].copy()

    if df.empty:
        return Paragraph(
            "Capital allocation data unavailable.",
            BODY_STYLE,
        )

    df["year_text"] = df["year"].astype(str).str.strip()

    df["year_num"] = pd.to_numeric(
        df["year_text"].str.extract(r"(20\d{2}|19\d{2})")[0],
        errors="coerce",
    )

    march = df[df["year_text"].str.lower().str.startswith("mar")].copy()

    if not march.empty:
        march = march.sort_values("year_num").drop_duplicates(
            subset=["year_num"],
            keep="last",
        )

        latest = march.iloc[-1]
    else:
        latest = df.iloc[-1]

    pattern = str(
        latest.get(
            "pattern_label",
            "Mixed",
        )
    )

    badge = Table(
        [
            [
                Paragraph(
                    f"<b>Capital Allocation: {pattern}</b>",
                    BODY_STYLE,
                )
            ]
        ],
        colWidths=[174 * mm],
        rowHeights=[12 * mm],
    )

    badge.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#FFF2CC"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.HexColor("#C9B458"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
            ]
        )
    )

    return badge


# -------------------------------------------------------------------
# PDF generation
# -------------------------------------------------------------------
def financial_health_summary(ratios):
    if ratios.empty:
        return Paragraph(
            "Financial health data unavailable.",
            BODY_STYLE,
        )

    latest = latest_row(ratios)

    if latest is None:
        return Paragraph(
            "Financial health data unavailable.",
            BODY_STYLE,
        )

    def fmt(name, value):
        if pd.isna(value):
            return "N/A"

        if name == "D/E":
            return f"{float(value):.2f}"

        if name == "FCF":
            return f"{float(value):,.0f} Cr"

        return f"{float(value):.1f}%"

    rows = [
        [
            Paragraph("<b>ROE</b>", BODY_STYLE),
            Paragraph(fmt("ROE", latest.get("return_on_equity_pct")), BODY_STYLE),
            Paragraph("<b>ROCE</b>", BODY_STYLE),
            Paragraph(
                fmt("ROCE", latest.get("return_on_capital_employed_pct")), BODY_STYLE
            ),
            Paragraph("<b>D/E</b>", BODY_STYLE),
            Paragraph(fmt("D/E", latest.get("debt_to_equity")), BODY_STYLE),
        ],
        [
            Paragraph("<b>Net Margin</b>", BODY_STYLE),
            Paragraph(
                fmt("Net Margin", latest.get("net_profit_margin_pct")), BODY_STYLE
            ),
            Paragraph("<b>Op. Margin</b>", BODY_STYLE),
            Paragraph(
                fmt("Op. Margin", latest.get("operating_profit_margin_pct")), BODY_STYLE
            ),
            Paragraph("<b>FCF</b>", BODY_STYLE),
            Paragraph(fmt("FCF", latest.get("free_cash_flow_cr")), BODY_STYLE),
        ],
    ]

    table = Table(
        rows,
        colWidths=[
            24 * mm,
            22 * mm,
            28 * mm,
            22 * mm,
            18 * mm,
            24 * mm,
        ],
        rowHeights=[6 * mm, 6 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF0F6")),
                ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#EAF0F6")),
                ("BACKGROUND", (4, 0), (4, -1), colors.HexColor("#EAF0F6")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C4D0")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D5DCE3")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    return table


def build_tearsheet(company_id: str):
    data = load_company_data(company_id)

    company = data["company"]

    if company.empty:
        raise ValueError(f"Company not found: {company_id}")

    company_name = get_company_name(data)
    sector = get_sector(data)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = OUTPUT_DIR / f"{company_id}_tearsheet.pdf"

    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=8 * mm,
        bottomMargin=8 * mm,
        title=f"{company_id} Company Tearsheet",
        author="N100 Financial Intelligence",
    )

    story = []

    # ---------------------------------------------------------------
    # PAGE 1
    # ---------------------------------------------------------------

    story.append(
        header_block(
            company_name,
            company_id,
            sector,
        )
    )

    story.append(Spacer(1, 5))

    story.append(
        Paragraph(
            "Key Performance Indicators",
            SECTION_STYLE,
        )
    )

    story.append(kpi_tiles(data["ratios"]))

    story.append(Spacer(1, 5))

    story.append(
        Paragraph(
            "Growth & Profitability",
            SECTION_STYLE,
        )
    )

    story.append(revenue_profit_chart(data["pnl"]))

    story.append(Spacer(1, 20))

    story.append(roe_roce_chart(data["ratios"]))

    story.append(PageBreak())

    # ---------------------------------------------------------------
    # PAGE 2
    # ---------------------------------------------------------------

    story.append(
        header_block(
            company_name,
            company_id,
            sector,
        )
    )

    story.append(Spacer(1, 4))

    story.append(
        Paragraph(
            "Balance Sheet Snapshot",
            SECTION_STYLE,
        )
    )

    story.append(balance_sheet_table(data["balance"]))

    story.append(Spacer(1, 5))

    story.append(
        Paragraph(
            "Cash Flow Snapshot",
            SECTION_STYLE,
        )
    )

    story.append(cash_flow_table(data["cashflow"]))

    story.append(Spacer(1, 5))

    story.append(
        Paragraph(
            "Pros & Cons",
            SECTION_STYLE,
        )
    )

    story.append(pros_cons_table(company_id))

    story.append(Spacer(1, 5))

    story.append(
        Paragraph(
            "Capital Allocation",
            SECTION_STYLE,
        )
    )

    story.append(capital_allocation_badge(company_id))

    story.append(Spacer(1, 3))

    story.append(
        Paragraph(
            "Financial Health Summary",
            SECTION_STYLE,
        )
    )

    story.append(financial_health_summary(data["ratios"]))

    doc.build(story)

    return output_file


# -------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------

if __name__ == "__main__":
    ticker = "TCS"

    output = build_tearsheet(ticker)

    print("=" * 60)
    print("DAY 33 - COMPANY TEARSHEET")
    print("=" * 60)
    print(f"Company: {ticker}")
    print(f"PDF: {output}")
    print(f"Size: {output.stat().st_size / 1024:.1f} KB")
    print("=" * 60)
