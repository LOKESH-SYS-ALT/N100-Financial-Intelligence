"""
N100 Financial Intelligence
Sprint 2 - Day 12
Financial Ratio Population Engine

Populates financial_ratios for every available company-year combination.
Also generates:
    output/capital_allocation.csv
    output/ratio_edge_cases.log
"""

from __future__ import annotations

import csv
import math
import re
import sqlite3
from pathlib import Path
from typing import Optional


def normalize_year(value):
    """
    Convert financial year values into a 4-digit year.

    Examples:
        2012        -> 2012
        "2012"      -> 2012
        "Dec 2012"  -> 2012
        "Mar 2024"  -> 2024
        "FY 2024"   -> 2024
        "TTM"       -> None
    """
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    if text.upper() == "TTM":
        return None

    match = re.search(r"\b(19|20)\d{2}\b", text)

    if match:
        return int(match.group(0))

    return None


DB_PATH = Path("data/nifty100.db")
OUTPUT_DIR = Path("output")


REQUIRED_COLUMNS = {
    "return_on_capital_employed_pct": "REAL",
    "return_on_assets_pct": "REAL",
    "revenue_cagr_5yr": "REAL",
    "pat_cagr_5yr": "REAL",
    "eps_cagr_5yr": "REAL",
    "composite_quality_score": "REAL",
    "high_leverage_flag": "INTEGER",
    "icr_label": "TEXT",
    "icr_warning_flag": "INTEGER",
    "revenue_cagr_5yr_flag": "TEXT",
    "pat_cagr_5yr_flag": "TEXT",
    "eps_cagr_5yr_flag": "TEXT",
}


def clean_number(value) -> Optional[float]:
    if value is None:
        return None

    try:
        value = float(value)

        if math.isnan(value) or math.isinf(value):
            return None

        return value

    except (TypeError, ValueError):
        return None


def safe_divide(a, b) -> Optional[float]:
    a = clean_number(a)
    b = clean_number(b)

    if a is None or b is None or b == 0:
        return None

    return a / b


def percentage(a, b) -> Optional[float]:
    result = safe_divide(a, b)

    if result is None:
        return None

    return result * 100


def cagr(start, end, years):
    """
    CAGR with all Sprint-2 edge cases.

    Returns:
        (value, flag)
    """
    start = clean_number(start)
    end = clean_number(end)

    if years is None or years <= 0:
        return None, "INSUFFICIENT"

    if start is None or end is None:
        return None, "INSUFFICIENT"

    if start == 0:
        return None, "ZERO_BASE"

    if start > 0 and end > 0:
        value = ((end / start) ** (1 / years) - 1) * 100
        return value, None

    if start > 0 and end < 0:
        return None, "DECLINE_TO_LOSS"

    if start < 0 and end > 0:
        return None, "TURNAROUND"

    if start < 0 and end < 0:
        return None, "BOTH_NEGATIVE"

    return None, "INSUFFICIENT"


def get_sector_map(con):
    """
    Dynamically reads sectors table.

    Supports common schemas such as:
        company_id, broad_sector
        company_id, sector
        id, broad_sector
    """
    try:
        columns = [
            row[1] for row in con.execute("PRAGMA table_info(sectors)").fetchall()
        ]

    except sqlite3.Error:
        return {}

    if not columns:
        return {}

    company_col = None
    sector_col = None

    for candidate in ("company_id", "id", "company"):
        if candidate in columns:
            company_col = candidate
            break

    for candidate in ("broad_sector", "sector", "sector_name"):
        if candidate in columns:
            sector_col = candidate
            break

    if company_col is None or sector_col is None:
        return {}

    rows = con.execute(f"""
        SELECT "{company_col}", "{sector_col}"
        FROM sectors
        """).fetchall()

    return {str(company_id): str(sector or "") for company_id, sector in rows}


def ensure_columns(con):
    existing = {
        row[1] for row in con.execute("PRAGMA table_info(financial_ratios)").fetchall()
    }

    for column, data_type in REQUIRED_COLUMNS.items():
        if column not in existing:
            con.execute(f"""
                ALTER TABLE financial_ratios
                ADD COLUMN {column} {data_type}
                """)

    con.commit()


def load_source_data(con):
    """
    Loads all source tables into dictionaries keyed by company_id/year.
    """

    profit_rows = con.execute("""
        SELECT
            company_id,
            year,
            sales,
            operating_profit,
            opm_percentage,
            other_income,
            interest,
            net_profit,
            eps,
            dividend_payout
        FROM profitandloss
        """).fetchall()

    balance_rows = con.execute("""
        SELECT
            company_id,
            year,
            equity_capital,
            reserves,
            borrowings,
            investments,
            total_assets
        FROM balancesheet
        """).fetchall()

    cash_rows = con.execute("""
        SELECT
            company_id,
            year,
            operating_activity,
            investing_activity,
            financing_activity
        FROM cashflow
        """).fetchall()

    company_rows = con.execute("""
        SELECT
            id,
            company_name,
            book_value,
            roce_percentage,
            roe_percentage,
            face_value
        FROM companies
        """).fetchall()

    profit = {}
    balance = {}
    cash = {}
    companies = {}

    for row in profit_rows:
        key = (str(row[0]), str(row[1]))
        profit[key] = row[2:]

    for row in balance_rows:
        key = (str(row[0]), str(row[1]))
        balance[key] = row[2:]

    for row in cash_rows:
        key = (str(row[0]), str(row[1]))
        cash[key] = row[2:]

    for row in company_rows:
        companies[str(row[0])] = {
            "name": row[1],
            "book_value": clean_number(row[2]),
            "roce_source": clean_number(row[3]),
            "roe_source": clean_number(row[4]),
            "face_value": clean_number(row[5]),
        }

    return profit, balance, cash, companies


def build_history(profit):
    """
    Builds company histories from profit-and-loss data.
    """
    history = {}

    for (company_id, year), values in profit.items():
        try:
            year_int = normalize_year(year)

        except (TypeError, ValueError):
            continue

        sales = clean_number(values[0])
        net_profit = clean_number(values[6])
        eps = clean_number(values[7])

        history.setdefault(company_id, []).append(
            {
                "year": year_int,
                "sales": sales,
                "net_profit": net_profit,
                "eps": eps,
            }
        )

    for company_id in history:
        history[company_id] = [
            row for row in history[company_id] if row.get("year") is not None
        ]

        history[company_id].sort(key=lambda x: x["year"])

    return history


def find_cagr(history, current_year, field, window):
    """
    Finds the exact historical point window years before current year.
    """

    if current_year is None:
        return None, "INSUFFICIENT"

    target_year = current_year - window

    current = None
    previous = None

    for row in history:
        if row["year"] == current_year:
            current = row.get(field)

        if row["year"] == target_year:
            previous = row.get(field)

    if current is None or previous is None:
        return None, "INSUFFICIENT"

    return cagr(previous, current, window)


def capital_allocation_pattern(
    cfo,
    cfi,
    cff,
    cfo_pat_ratio=None,
):
    def sign(value):
        value = clean_number(value)

        if value is None or value == 0:
            return "0"

        return "+" if value > 0 else "-"

    cfo_sign = sign(cfo)
    cfi_sign = sign(cfi)
    cff_sign = sign(cff)

    pattern = (
        cfo_sign,
        cfi_sign,
        cff_sign,
    )

    if pattern == ("+", "-", "-"):
        if cfo_pat_ratio is not None and cfo_pat_ratio > 1:
            label = "Shareholder Returns"
        else:
            label = "Reinvestor"

    elif pattern == ("+", "+", "-"):
        label = "Liquidating Assets"

    elif pattern == ("-", "+", "+"):
        label = "Distress Signal"

    elif pattern == ("-", "-", "+"):
        label = "Growth Funded by Debt"

    elif pattern == ("+", "+", "+"):
        label = "Cash Accumulator"

    elif pattern == ("-", "-", "-"):
        label = "Pre-Revenue"

    elif pattern == ("+", "-", "+"):
        label = "Mixed"

    else:
        label = "Mixed"

    return (
        cfo_sign,
        cfi_sign,
        cff_sign,
        label,
    )


def quality_score(
    roe,
    net_margin,
    debt_equity,
    icr,
    revenue_cagr,
):
    """
    Simple 0-100 composite score.

    Each component contributes up to 20 points.
    """
    score = 0.0

    roe = clean_number(roe)
    net_margin = clean_number(net_margin)
    debt_equity = clean_number(debt_equity)
    icr = clean_number(icr)
    revenue_cagr = clean_number(revenue_cagr)

    if roe is not None:
        if roe >= 20:
            score += 20
        elif roe >= 15:
            score += 15
        elif roe >= 10:
            score += 10
        elif roe > 0:
            score += 5

    if net_margin is not None:
        if net_margin >= 20:
            score += 20
        elif net_margin >= 10:
            score += 15
        elif net_margin >= 5:
            score += 10
        elif net_margin > 0:
            score += 5

    if debt_equity is not None:
        if debt_equity <= 0.5:
            score += 20
        elif debt_equity <= 1:
            score += 15
        elif debt_equity <= 2:
            score += 10
        elif debt_equity <= 5:
            score += 5

    if icr is not None:
        if icr >= 5:
            score += 20
        elif icr >= 3:
            score += 15
        elif icr >= 1.5:
            score += 10
        elif icr > 0:
            score += 5
    else:
        score += 20

    if revenue_cagr is not None:
        if revenue_cagr >= 15:
            score += 20
        elif revenue_cagr >= 10:
            score += 15
        elif revenue_cagr >= 5:
            score += 10
        elif revenue_cagr > 0:
            score += 5

    return round(score, 2)


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys=ON")

    print("=" * 60)
    print("N100 FINANCIAL INTELLIGENCE")
    print("SPRINT 2 - FINANCIAL RATIO ENGINE")
    print("=" * 60)

    ensure_columns(con)

    profit, balance, cash, companies = load_source_data(con)
    sector_map = get_sector_map(con)
    history = build_history(profit)

    print(f"Profit/Loss rows: {len(profit)}")
    print(f"Balance Sheet rows: {len(balance)}")
    print(f"Cash Flow rows: {len(cash)}")
    print(f"Companies: {len(companies)}")

    keys = sorted(set(profit.keys()) | set(balance.keys()) | set(cash.keys()))

    print(f"Available company-year combinations: " f"{len(keys)}")

    con.execute("DELETE FROM financial_ratios")

    edge_cases = []
    allocation_rows = []

    insert_sql = """
        INSERT INTO financial_ratios (
            company_id,
            year,
            net_profit_margin_pct,
            operating_profit_margin_pct,
            return_on_equity_pct,
            debt_to_equity,
            interest_coverage,
            asset_turnover,
            free_cash_flow_cr,
            capex_cr,
            earnings_per_share,
            book_value_per_share,
            dividend_payout_ratio_pct,
            total_debt_cr,
            cash_from_operations_cr,
            return_on_capital_employed_pct,
            return_on_assets_pct,
            revenue_cagr_5yr,
            pat_cagr_5yr,
            eps_cagr_5yr,
            composite_quality_score,
            high_leverage_flag,
            icr_label,
            icr_warning_flag,
            revenue_cagr_5yr_flag,
            pat_cagr_5yr_flag,
            eps_cagr_5yr_flag
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """

    inserted = 0

    for company_id, year in keys:
        p = profit.get((company_id, year))

        b = balance.get((company_id, year))

        cf = cash.get((company_id, year))

        p = p or (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

        b = b or (
            None,
            None,
            None,
            None,
            None,
        )

        cf = cf or (
            None,
            None,
            None,
        )

        sales = clean_number(p[0])
        operating_profit = clean_number(p[1])
        source_opm = clean_number(p[2])
        other_income = clean_number(p[3])
        interest = clean_number(p[4])
        net_profit = clean_number(p[5])
        eps = clean_number(p[6])
        dividend_payout = clean_number(p[7])

        equity_capital = clean_number(b[0])
        reserves = clean_number(b[1])
        borrowings = clean_number(b[2])
        investments = clean_number(b[3])
        total_assets = clean_number(b[4])

        cfo = clean_number(cf[0])
        cfi = clean_number(cf[1])
        cff = clean_number(cf[2])

        equity = None

        if equity_capital is not None and reserves is not None:
            equity = equity_capital + reserves

        capital_employed = None

        if equity is not None and borrowings is not None:
            capital_employed = equity + borrowings

        npm = percentage(
            net_profit,
            sales,
        )

        opm = percentage(
            operating_profit,
            sales,
        )

        roe = percentage(
            net_profit,
            equity,
        )

        roce = percentage(
            operating_profit,
            capital_employed,
        )

        roa = percentage(
            net_profit,
            total_assets,
        )

        de = safe_divide(
            borrowings,
            equity,
        )

        if borrowings == 0:
            de = 0.0

        icr = None

        if interest is not None and interest != 0:
            numerator = 0

            if operating_profit is not None:
                numerator += operating_profit

            if other_income is not None:
                numerator += other_income

            icr = safe_divide(
                numerator,
                interest,
            )

        icr_label_value = "Debt Free" if icr is None else "Covered"

        icr_warning = icr is not None and icr < 1.5

        sector = sector_map.get(
            company_id,
            "",
        )

        is_financials = str(sector).strip().lower() == "financials"

        high_leverage = de is not None and de > 5 and not is_financials

        if is_financials and de is not None and de > 5:
            edge_cases.append(
                f"{company_id},{year}: "
                "Financials high leverage flag "
                "suppressed by sector carve-out."
            )

        asset_turnover_value = safe_divide(
            sales,
            total_assets,
        )

        fcf = None

        if cfo is not None and cfi is not None:
            fcf = cfo + cfi

        capex = None

        if cfi is not None:
            capex = abs(cfi)

        book_value = companies.get(
            company_id,
            {},
        ).get("book_value")

        current_year = normalize_year(year)

        revenue_cagr, revenue_flag = find_cagr(
            history.get(
                company_id,
                [],
            ),
            current_year,
            "sales",
            5,
        )

        pat_cagr, pat_flag = find_cagr(
            history.get(
                company_id,
                [],
            ),
            current_year,
            "net_profit",
            5,
        )

        eps_cagr, eps_flag = find_cagr(
            history.get(
                company_id,
                [],
            ),
            current_year,
            "eps",
            5,
        )

        if opm is not None and source_opm is not None:
            difference = abs(opm - source_opm)

            if difference > 1:
                edge_cases.append(
                    f"{company_id},{year}: "
                    f"OPM mismatch "
                    f"computed={opm:.4f}, "
                    f"source={source_opm:.4f}, "
                    f"difference={difference:.4f}%"
                )

        source_roce = companies.get(
            company_id,
            {},
        ).get("roce_source")

        if roce is not None and source_roce is not None:
            difference = abs(roce - source_roce)

            if difference > 5:
                edge_cases.append(
                    f"{company_id},{year}: "
                    f"ROCE anomaly "
                    f"computed={roce:.4f}, "
                    f"source={source_roce:.4f}, "
                    f"difference={difference:.4f}%; "
                    "category=requires_review"
                )

        source_roe = companies.get(
            company_id,
            {},
        ).get("roe_source")

        if roe is not None and source_roe is not None:
            difference = abs(roe - source_roe)

            if difference > 5:
                edge_cases.append(
                    f"{company_id},{year}: "
                    f"ROE anomaly "
                    f"computed={roe:.4f}, "
                    f"source={source_roe:.4f}, "
                    f"difference={difference:.4f}%; "
                    "category=requires_review"
                )

        cfo_pat_ratio = safe_divide(
            cfo,
            net_profit,
        )

        (
            cfo_sign,
            cfi_sign,
            cff_sign,
            pattern_label,
        ) = capital_allocation_pattern(
            cfo,
            cfi,
            cff,
            cfo_pat_ratio,
        )

        allocation_rows.append(
            {
                "company_id": company_id,
                "year": year,
                "cfo_sign": cfo_sign,
                "cfi_sign": cfi_sign,
                "cff_sign": cff_sign,
                "pattern_label": pattern_label,
            }
        )

        score = quality_score(
            roe,
            npm,
            de,
            icr,
            revenue_cagr,
        )

        con.execute(
            insert_sql,
            (
                company_id,
                year,
                npm,
                opm,
                roe,
                de,
                icr,
                asset_turnover_value,
                fcf,
                capex,
                eps,
                book_value,
                dividend_payout,
                borrowings,
                cfo,
                roce,
                roa,
                revenue_cagr,
                pat_cagr,
                eps_cagr,
                score,
                int(high_leverage),
                icr_label_value,
                int(icr_warning),
                revenue_flag,
                pat_flag,
                eps_flag,
            ),
        )

        inserted += 1

    con.commit()

    allocation_path = OUTPUT_DIR / "capital_allocation.csv"

    with allocation_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "company_id",
                "year",
                "cfo_sign",
                "cfi_sign",
                "cff_sign",
                "pattern_label",
            ],
        )

        writer.writeheader()
        writer.writerows(allocation_rows)

    edge_path = OUTPUT_DIR / "ratio_edge_cases.log"

    with edge_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            "N100 Financial Intelligence\n"
            "Sprint 2 - Ratio Edge Cases\n" + "=" * 70 + "\n"
        )

        if not edge_cases:
            file.write("No anomalies detected.\n")
        else:
            for item in edge_cases:
                file.write(item + "\n")

    row_count = con.execute("SELECT COUNT(*) " "FROM financial_ratios").fetchone()[0]

    print()
    print("=" * 60)
    print("POPULATION COMPLETE")
    print("=" * 60)
    print(f"Inserted rows: {inserted}")
    print(f"Database rows: {row_count}")
    print(f"Capital allocation rows: " f"{len(allocation_rows)}")
    print(f"Edge-case entries: " f"{len(edge_cases)}")

    columns = [
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "capex_cr",
        "earnings_per_share",
        "book_value_per_share",
        "dividend_payout_ratio_pct",
        "total_debt_cr",
        "cash_from_operations_cr",
        "return_on_capital_employed_pct",
        "return_on_assets_pct",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score",
    ]

    print()
    print("Null-only KPI columns:")

    for column in columns:
        count = con.execute(f"""
            SELECT COUNT(*)
            FROM financial_ratios
            WHERE {column} IS NOT NULL
            """).fetchone()[0]

        print(
            f"  {column}: "
            f"{'OK' if count > 0 else 'NULL-ONLY'} "
            f"({count} populated)"
        )

    fk_errors = con.execute("PRAGMA foreign_key_check").fetchall()

    print()
    print(f"Foreign key errors: " f"{len(fk_errors)}")

    con.close()

    print()
    print("Generated:")
    print(f"  {allocation_path}")
    print(f"  {edge_path}")


if __name__ == "__main__":
    main()
