from pathlib import Path
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB = PROJECT_ROOT / "data" / "nifty100.db"
OUT = PROJECT_ROOT / "reports" / "portfolio"
OUT.mkdir(parents=True, exist_ok=True)

PDF = OUT / "portfolio_summary.pdf"


def num(value):
    try:
        if pd.isna(value):
            return "N/A"
        return f"{float(value):.2f}"
    except:
        return "N/A"


def arrow(current, previous):
    try:
        current = float(current)
        previous = float(previous)

        if previous == 0:
            return "N/A"

        change = (current - previous) / abs(previous) * 100

        if change > 2:
            return "UP"
        if change < -2:
            return "DOWN"
        return "FLAT"

    except:
        return "N/A"


def get_latest_rows(ratios):
    rows = []

    for ticker in sorted(ratios["company_id"].astype(str).unique()):
        df = ratios[ratios["company_id"].astype(str) == ticker].copy()

        df["year_text"] = df["year"].astype(str)

        annual = df[
            df["year_text"].str.match(r"^Mar\s+\d{4}$", case=False, na=False)
        ].copy()

        if annual.empty:
            annual = df.copy()

        annual["year_num"] = pd.to_numeric(
            annual["year_text"].str.extract(r"(\d{4})")[0], errors="coerce"
        )

        annual = annual.sort_values("year_num")

        if annual.empty:
            continue

        latest = annual.iloc[-1]
        previous = annual.iloc[-2] if len(annual) >= 2 else None

        rows.append((ticker, latest, previous))

    return rows


def main():
    conn = sqlite3.connect(DB)

    companies = pd.read_sql(
        """
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector AS sector
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        ORDER BY c.id
    """,
        conn,
    )

    ratios = pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
    """,
        conn,
    )

    conn.close()

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "PortfolioTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=26,
        spaceAfter=10,
    )

    subtitle = ParagraphStyle(
        "PortfolioSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        spaceAfter=14,
    )

    small = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
    )

    doc = SimpleDocTemplate(
        str(PDF),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    story = []

    latest_rows = get_latest_rows(ratios)

    latest_map = {
        ticker: (latest, previous) for ticker, latest, previous in latest_rows
    }

    generated = 0

    for _, company in companies.sort_values("company_id").iterrows():

        ticker = str(company["company_id"])
        name = str(company["company_name"])
        sector = str(company["sector"]) if pd.notna(company["sector"]) else "N/A"

        latest, previous = latest_map.get(ticker, ({}, None))

        story.append(Paragraph("N100 FINANCIAL INTELLIGENCE", title))

        story.append(Paragraph(f"<b>{ticker}</b> — {name}", subtitle))

        story.append(Paragraph(f"Sector: <b>{sector}</b>", styles["Heading3"]))

        story.append(Spacer(1, 10))

        kpis = [
            ("ROE", "return_on_equity_pct"),
            ("ROCE", "return_on_capital_employed_pct"),
            ("D/E", "debt_to_equity"),
            ("Revenue CAGR", "revenue_cagr_5yr"),
            ("PAT CAGR", "pat_cagr_5yr"),
            ("EPS CAGR", "eps_cagr_5yr"),
        ]

        kpi_data = [["KPI", "Latest", "Trend"]]

        for label, column in kpis:
            current = latest.get(column) if hasattr(latest, "get") else None
            prior = (
                previous.get(column)
                if previous is not None and hasattr(previous, "get")
                else None
            )

            kpi_data.append(
                [
                    label,
                    num(current),
                    arrow(current, prior),
                ]
            )

        table = Table(
            kpi_data,
            colWidths=[180, 140, 80],
            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 20))

        story.append(
            Paragraph(
                f"Latest annual period: {latest.get('year', 'N/A') if hasattr(latest, 'get') else 'N/A'}",
                small,
            )
        )

        story.append(Spacer(1, 10))

        story.append(
            Paragraph("Trend rule: ? improved, ? declined, ? flat within ±2%.", small)
        )

        generated += 1

        if generated < len(companies):
            story.append(PageBreak())

    doc.build(story)

    print("=" * 60)
    print("DAY 35 - PORTFOLIO SUMMARY")
    print("=" * 60)
    print(f"Companies in DB : {len(companies)}")
    print(f"Pages generated : {generated}")
    print(f"PDF             : {PDF}")
    print(f"PDF size        : {PDF.stat().st_size} bytes")
    print("=" * 60)


if __name__ == "__main__":
    main()
