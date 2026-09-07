from pathlib import Path
import sqlite3
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB = PROJECT_ROOT / "data" / "nifty100.db"
OUT = PROJECT_ROOT / "reports" / "sector"
OUT.mkdir(parents=True, exist_ok=True)

def clean_number(value):
    try:
        if pd.isna(value):
            return "N/A"
        return f"{float(value):.2f}"
    except:
        return "N/A"

def build_sector_report(sector, companies, ratios):
    safe_name = "".join(
        c if c.isalnum() or c in (" ", "_", "-") else "_"
        for c in sector
    ).strip().replace(" ", "_")

    pdf_path = OUT / f"{safe_name}_report.pdf"

    sector_companies = companies[
        companies["broad_sector"] == sector
    ].copy()

    sector_ratios = ratios[
        ratios["company_id"].isin(sector_companies["company_id"])
    ].copy()

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=28,
        leftMargin=28,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "SectorTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=12,
    )

    story = []

    story.append(Paragraph(
        f"N100 FINANCIAL INTELLIGENCE — {sector}",
        title_style
    ))
    story.append(Paragraph(
        f"Companies covered: {len(sector_companies)}",
        styles["Heading2"]
    ))
    story.append(Spacer(1, 12))

    median_columns = [
        ("ROE", "return_on_equity_pct"),
        ("ROCE", "return_on_capital_employed_pct"),
        ("D/E", "debt_to_equity"),
        ("Revenue CAGR", "revenue_cagr_5yr"),
        ("PAT CAGR", "pat_cagr_5yr"),
        ("EPS CAGR", "eps_cagr_5yr"),
    ]

    summary_data = [["Metric", "Sector Median"]]

    for label, column in median_columns:
        if column in sector_ratios.columns:
            value = pd.to_numeric(
                sector_ratios[column],
                errors="coerce"
            ).median()
        else:
            value = None

        summary_data.append([label, clean_number(value)])

    story.append(Paragraph("Sector Median KPIs", styles["Heading2"]))

    summary_table = Table(
        summary_data,
        colWidths=[220, 180],
        repeatRows=1,
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 18))

    story.append(Paragraph("Company Intelligence", styles["Heading2"]))

    company_rows = [[
        "Company",
        "ROE",
        "ROCE",
        "D/E",
        "Rev CAGR",
        "PAT CAGR",
        "EPS CAGR",
        "Quality",
    ]]

    latest_rows = (
        sector_ratios[
            sector_ratios["year"].astype(str).str.upper().eq("TTM")
        ]
        .copy()
    )

    for _, company in sector_companies.sort_values("company_id").iterrows():
        ticker = company["company_id"]

        row = latest_rows[
            latest_rows["company_id"].astype(str) == str(ticker)
        ]

        if row.empty:
            row = sector_ratios[
                sector_ratios["company_id"].astype(str) == str(ticker)
            ].tail(1)

        if row.empty:
            values = {}
        else:
            values = row.iloc[-1].to_dict()

        company_rows.append([
            str(ticker),
            clean_number(values.get("return_on_equity_pct")),
            clean_number(values.get("return_on_capital_employed_pct")),
            clean_number(values.get("debt_to_equity")),
            clean_number(values.get("revenue_cagr_5yr")),
            clean_number(values.get("pat_cagr_5yr")),
            clean_number(values.get("eps_cagr_5yr")),
            clean_number(values.get("composite_quality_score")),
        ])

    company_table = Table(
        company_rows,
        colWidths=[75, 45, 48, 42, 52, 52, 52, 52],
        repeatRows=1,
    )

    company_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))

    story.append(company_table)

    doc.build(story)

    return pdf_path

def main():
    conn = sqlite3.connect(DB)

    companies = pd.read_sql("""
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE s.broad_sector IS NOT NULL
        ORDER BY s.broad_sector, c.id
    """, conn)

    ratios = pd.read_sql("""
        SELECT *
        FROM financial_ratios
    """, conn)

    conn.close()

    sectors = sorted(
        companies["broad_sector"].dropna().unique()
    )

    print("=" * 60)
    print("DAY 34 - SECTOR REPORTS")
    print("=" * 60)
    print(f"Sectors found: {len(sectors)}")

    generated = 0
    errors = []

    for sector in sectors:
        try:
            pdf = build_sector_report(
                sector,
                companies,
                ratios
            )
            generated += 1
            print(f"OK  {sector}  {pdf.stat().st_size} bytes")
        except Exception as e:
            errors.append({
                "sector": sector,
                "error": str(e)
            })
            print(f"ERROR  {sector}: {e}")

    print("=" * 60)
    print(f"Generated sector PDFs : {generated}")
    print(f"Errors                : {len(errors)}")
    print(f"Output                : {OUT}")

    if errors:
        pd.DataFrame(errors).to_csv(
            PROJECT_ROOT / "output" / "sector_report_errors.csv",
            index=False
        )

    print("=" * 60)

if __name__ == "__main__":
    main()
