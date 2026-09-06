import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"


def get_connection():
    return sqlite3.connect(DB_PATH)

def get_valuation_data():
    conn = get_connection()

    query = """
        SELECT
            mc.company_id,
            c.company_name,
            mc.year,
            mc.market_cap_crore,
            mc.enterprise_value_crore,
            mc.pe_ratio,
            mc.pb_ratio,
            mc.ev_ebitda,
            mc.dividend_yield_pct,
            fr.free_cash_flow_cr,
            fr.earnings_per_share,
            fr.book_value_per_share
        FROM market_cap mc
        LEFT JOIN companies c
            ON mc.company_id = c.id
        LEFT JOIN financial_ratios fr
            ON fr.company_id = mc.company_id
            AND fr.year = 'TTM'
        ORDER BY mc.company_id, mc.year
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df

def calculate_fcf_yield(df):
    df = df.copy()

    df["fcf_yield_pct"] = (
        df["free_cash_flow_cr"]
        / df["market_cap_crore"]
        * 100
    )

    return df
def pe_flag(pe):
    if pd.isna(pe):
        return "N/A"

    if pe <= 15:
        return "Cheap"

    if pe <= 25:
        return "Fair"

    return "Expensive"


def valuation_label(row):
    pe = row.get("pe_ratio")
    fcf_yield = row.get("fcf_yield_pct")

    if pd.isna(pe) and pd.isna(fcf_yield):
        return "N/A"

    if pd.notna(pe) and pe <= 15:
        return "Undervalued"

    if pd.notna(fcf_yield) and fcf_yield >= 5:
        return "Undervalued"

    if pd.notna(pe) and pe > 40:
        return "Overvalued"

    if pd.notna(fcf_yield) and fcf_yield < 2:
        return "Overvalued"

    return "Fair Value"


def build_valuation_summary():
    df = get_valuation_data()

    if df.empty:
        return df

    df = calculate_fcf_yield(df)

    df["pe_flag"] = df["pe_ratio"].apply(pe_flag)

    df["valuation_label"] = df.apply(
        valuation_label,
        axis=1,
    )

    return df


def export_valuation_summary(
    output_path="output/valuation_summary.xlsx",
):
    df = build_valuation_summary()

    if df.empty:
        raise ValueError(
            "No valuation data available."
        )

    output_file = PROJECT_ROOT / output_path

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_excel(
        output_file,
        index=False,
    )

    return output_file


if __name__ == "__main__":
    summary = build_valuation_summary()

    print(
        f"Valuation rows: {len(summary)}"
    )

    if not summary.empty:
        print(
            summary[
                [
                    "company_id",
                    "year",
                    "pe_ratio",
                    "fcf_yield_pct",
                    "pe_flag",
                    "valuation_label",
                ]
            ].head(10).to_string(index=False)
        )

    output_file = export_valuation_summary()

    print(
        f"Excel created: {output_file}"
    )