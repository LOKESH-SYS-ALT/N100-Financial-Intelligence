"""
N100 Financial Intelligence
Sprint 2 - Cash Flow KPIs

Day 11:
- Free Cash Flow
- CFO Quality
- CapEx Intensity
- FCF Conversion
- Capital Allocation Pattern
"""

from typing import Optional


# ============================================================
# FREE CASH FLOW
# ============================================================

def free_cash_flow(
    operating_activity: float,
    investing_activity: float,
) -> float:
    """
    Free Cash Flow = Operating Cash Flow + Investing Cash Flow.

    Negative FCF is valid and is not treated as an error.
    """
    return operating_activity + investing_activity


# ============================================================
# CFO QUALITY
# ============================================================

def cfo_pat_ratio(
    cash_from_operations: float,
    net_profit: float,
) -> Optional[float]:
    """
    CFO / PAT.

    PAT = 0 -> None.
    """
    if net_profit == 0:
        return None

    return cash_from_operations / net_profit


def average_cfo_pat_ratio(
    cfo_values: list[float],
    pat_values: list[float],
) -> Optional[float]:
    """
    Average CFO/PAT ratio over available years.

    Years where PAT = 0 are ignored.
    Returns None when no valid ratio exists.
    """
    ratios = []

    for cfo, pat in zip(cfo_values, pat_values):
        ratio = cfo_pat_ratio(cfo, pat)

        if ratio is not None:
            ratios.append(ratio)

    if not ratios:
        return None

    return sum(ratios) / len(ratios)


def cfo_quality_label(
    ratio: Optional[float],
) -> Optional[str]:
    """
    CFO Quality classification.

    > 1.0       -> High Quality
    0.5 to 1.0  -> Moderate
    < 0.5       -> Accrual Risk
    """
    if ratio is None:
        return None

    if ratio > 1.0:
        return "High Quality"

    if ratio >= 0.5:
        return "Moderate"

    return "Accrual Risk"


# ============================================================
# CAPEX INTENSITY
# ============================================================

def capex_intensity(
    investing_activity: float,
    sales: float,
) -> Optional[float]:
    """
    CapEx Intensity = abs(CFI) / Sales * 100.

    Sales = 0 -> None.
    """
    if sales == 0:
        return None

    return abs(investing_activity) / sales * 100


def capex_intensity_label(
    intensity: Optional[float],
) -> Optional[str]:
    """
    CapEx classification.

    < 3%     -> Asset Light
    3% - 8%   -> Moderate
    > 8%      -> Capital Intensive
    """
    if intensity is None:
        return None

    if intensity < 3:
        return "Asset Light"

    if intensity <= 8:
        return "Moderate"

    return "Capital Intensive"


# ============================================================
# FCF CONVERSION
# ============================================================

def fcf_conversion_rate(
    free_cash_flow_value: float,
    operating_profit: float,
) -> Optional[float]:
    """
    FCF Conversion Rate = FCF / Operating Profit * 100.

    Operating Profit = 0 -> None.
    """
    if operating_profit == 0:
        return None

    return free_cash_flow_value / operating_profit * 100


# ============================================================
# SIGN HELPERS
# ============================================================

def cash_flow_sign(value: float) -> str:
    """
    Convert cash-flow value into + or - sign.

    Zero is treated as + for stable classification.
    """
    if value >= 0:
        return "+"

    return "-"


# ============================================================
# CAPITAL ALLOCATION
# ============================================================

def capital_allocation_pattern(
    cfo: float,
    cfi: float,
    cff: float,
    cfo_pat_ratio_value: Optional[float] = None,
) -> str:
    """
    Classify capital allocation using CFO/CFI/CFF signs.

    Patterns:

    (+,-,-) -> Reinvestor
    (+,-,+) -> Mixed
    (+,+,-) -> Liquidating Assets
    (-,+,+) -> Distress Signal
    (-,-,+) -> Growth Funded by Debt
    (+,+,+) -> Cash Accumulator
    (-,-,-) -> Pre-Revenue

    For (+,-,-), a strong CFO/PAT ratio > 1.0
    is classified as Shareholder Returns.
    """

    pattern = (
        cash_flow_sign(cfo),
        cash_flow_sign(cfi),
        cash_flow_sign(cff),
    )

    if pattern == ("+", "-", "-"):
        if (
            cfo_pat_ratio_value is not None
            and cfo_pat_ratio_value > 1.0
        ):
            return "Shareholder Returns"

        return "Reinvestor"

    if pattern == ("+", "-", "+"):
        return "Mixed"

    if pattern == ("+", "+", "-"):
        return "Liquidating Assets"

    if pattern == ("-", "+", "+"):
        return "Distress Signal"

    if pattern == ("-", "-", "+"):
        return "Growth Funded by Debt"

    if pattern == ("+", "+", "+"):
        return "Cash Accumulator"

    if pattern == ("-", "-", "-"):
        return "Pre-Revenue"

    return "Mixed"


# ============================================================
# ALL DAY-11 KPIs
# ============================================================

def calculate_cashflow_kpis(
    operating_activity: float,
    investing_activity: float,
    financing_activity: float,
    sales: float,
    operating_profit: float,
    cfo_pat_ratio_value: Optional[float] = None,
) -> dict:
    """
    Calculate all Day-11 cash-flow KPIs.
    """

    fcf = free_cash_flow(
        operating_activity,
        investing_activity,
    )

    capex = capex_intensity(
        investing_activity,
        sales,
    )

    return {
        "free_cash_flow_cr": fcf,
        "cfo_pat_ratio": cfo_pat_ratio_value,
        "cfo_quality_label": cfo_quality_label(
            cfo_pat_ratio_value
        ),
        "capex_intensity_pct": capex,
        "capex_intensity_label": capex_intensity_label(
            capex
        ),
        "fcf_conversion_rate_pct": fcf_conversion_rate(
            fcf,
            operating_profit,
        ),
        "capital_allocation_pattern": capital_allocation_pattern(
            operating_activity,
            investing_activity,
            financing_activity,
            cfo_pat_ratio_value,
        ),
    }

# ============================================================
# SPRINT 5 - DAY 31
# CASH FLOW INTELLIGENCE
# ============================================================

from pathlib import Path
import sqlite3
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"


def load_day31_data():
    """
    Load cash flow, P&L and balance sheet data.
    """

    conn = sqlite3.connect(DB_PATH)

    cashflow = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            operating_activity,
            investing_activity,
            financing_activity,
            net_cash_flow
        FROM cashflow
        """,
        conn,
    )

    pnl = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            sales,
            operating_profit,
            net_profit
        FROM profitandloss
        """,
        conn,
    )

    balance = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            borrowings
        FROM balancesheet
        """,
        conn,
    )
    sectors = pd.read_sql(
    """
    SELECT
        company_id,
        broad_sector
    FROM sectors
    """,
    conn,
)
    conn.close()

    return cashflow, pnl, balance, sectors


def calculate_fcf_cagr_5yr(company_df):
    """
    FCF CAGR using approximately 5 years of data.

    FCF = CFO + CFI
    """

    df = company_df.copy()

    df["fcf"] = (
        pd.to_numeric(df["operating_activity"], errors="coerce")
        + pd.to_numeric(df["investing_activity"], errors="coerce")
    )

    df = df.dropna(subset=["fcf"])

    if len(df) < 2:
        return None

    df = df.sort_values("year")

    start = df.iloc[0]["fcf"]
    end = df.iloc[-1]["fcf"]

    if start <= 0 or end <= 0:
        return None

    years = len(df) - 1

    if years <= 0:
        return None

    return ((end / start) ** (1 / years) - 1) * 100


def calculate_distress_flag(latest):
    """
    Distress:
    CFO < 0 AND CFF > 0
    """

    return bool(
        latest["operating_activity"] < 0
        and latest["financing_activity"] > 0
    )


def calculate_deleveraging_flag(company_cashflow, company_balance):
    """
    Deleveraging:
    Latest CFF < 0 AND borrowings declining YoY.
    """

    if company_cashflow.empty or company_balance.empty:
        return False

    latest_cf = company_cashflow.sort_values("year").iloc[-1]

    if latest_cf["financing_activity"] >= 0:
        return False

    balance = company_balance.sort_values("year").copy()

    balance["borrowings"] = pd.to_numeric(
        balance["borrowings"],
        errors="coerce",
    )

    balance = balance.dropna(subset=["borrowings"])

    if len(balance) < 2:
        return False

    latest_borrowings = balance.iloc[-1]["borrowings"]
    previous_borrowings = balance.iloc[-2]["borrowings"]

    return bool(latest_borrowings < previous_borrowings)


def build_cashflow_intelligence():
    """
    Build one intelligence row for every company.
    """

    cashflow, pnl, balance, sectors = load_day31_data()

    results = []

    companies = sorted(
        set(cashflow["company_id"].dropna())
        | set(pnl["company_id"].dropna())
        | set(balance["company_id"].dropna())
    )

    for company_id in companies:

        cf = cashflow[
            cashflow["company_id"] == company_id
        ].copy()

        pl = pnl[
            pnl["company_id"] == company_id
        ].copy()

        bs = balance[
            balance["company_id"] == company_id
        ].copy()

        if cf.empty:
            continue

        cf = cf.sort_values("year")

        latest_cf = cf.iloc[-1]

        # ----------------------------------------------------
        # FCF
        # ----------------------------------------------------

        cf["fcf"] = (
            pd.to_numeric(
                cf["operating_activity"],
                errors="coerce",
            )
            +
            pd.to_numeric(
                cf["investing_activity"],
                errors="coerce",
            )
        )

        # ----------------------------------------------------
        # 5-YEAR WINDOW
        # ----------------------------------------------------

        five_year_cf = cf.tail(5)

        # ----------------------------------------------------
        # CFO / PAT
        # ----------------------------------------------------

        merged = pd.merge(
            five_year_cf[
                [
                    "year",
                    "operating_activity",
                ]
            ],
            pl[
                [
                    "year",
                    "net_profit",
                ]
            ],
            on="year",
            how="inner",
        )

        merged["operating_activity"] = pd.to_numeric(
            merged["operating_activity"],
            errors="coerce",
        )

        merged["net_profit"] = pd.to_numeric(
            merged["net_profit"],
            errors="coerce",
        )

        merged = merged.dropna(
            subset=[
                "operating_activity",
                "net_profit",
            ]
        )

        merged = merged[
            merged["net_profit"] != 0
        ]

        if not merged.empty:

            cfo_pat_values = (
                merged["operating_activity"]
                / merged["net_profit"]
            )

            cfo_quality_score = (
                cfo_pat_values.mean()
            )

            cfo_quality = cfo_quality_label(
                cfo_quality_score
            )

        else:

            cfo_quality_score = None
            cfo_quality = "Not Available"

        # ----------------------------------------------------
        # CAPEX INTENSITY
        # ----------------------------------------------------

        latest_pl = (
            pl.sort_values("year").iloc[-1]
            if not pl.empty
            else None
        )

        capex_intensity_pct = None
        capex_label = "Not Available"

        if latest_pl is not None:

            sales = pd.to_numeric(
                latest_pl["sales"],
                errors="coerce",
            )

            if pd.notna(sales) and sales != 0:

                capex_intensity_pct = (
                    abs(
                        latest_cf[
                            "investing_activity"
                        ]
                    )
                    / sales
                    * 100
                )

                capex_label = capex_intensity_label(
                    capex_intensity_pct
                )

        # ----------------------------------------------------
        # FCF CAGR
        # ----------------------------------------------------

        fcf_cagr = calculate_fcf_cagr_5yr(
            five_year_cf
        )

        # ----------------------------------------------------
        # FCF CONVERSION
        # ----------------------------------------------------

        fcf_conversion_pct = None

        if latest_pl is not None:

            operating_profit = pd.to_numeric(
                latest_pl["operating_profit"],
                errors="coerce",
            )

            latest_fcf = (
    pd.to_numeric(latest_cf["operating_activity"], errors="coerce")
    + pd.to_numeric(latest_cf["investing_activity"], errors="coerce")
)

            if (
                pd.notna(operating_profit)
                and operating_profit != 0
            ):

                fcf_conversion_pct = (
                    latest_fcf
                    / operating_profit
                    * 100
                )

        # ----------------------------------------------------
        # DISTRESS
        # ----------------------------------------------------

        distress_flag = calculate_distress_flag(
            latest_cf
        )

        # ----------------------------------------------------
        # DELEVERAGING
        # ----------------------------------------------------

        deleveraging_flag = (
            calculate_deleveraging_flag(
                cf,
                bs,
            )
        )

        # ----------------------------------------------------
        # CAPITAL ALLOCATION
        # ----------------------------------------------------

        capital_label = capital_allocation_pattern(
            latest_cf["operating_activity"],
            latest_cf["investing_activity"],
            latest_cf["financing_activity"],
            cfo_quality_score,
        )
        # ----------------------------------------------------
        # SECTOR
        # ----------------------------------------------------

        sector_row = sectors[
            sectors["company_id"] == company_id
        ]

        if not sector_row.empty:
            sector = sector_row.iloc[0]["broad_sector"]
        else:
            sector = "Unknown"

        results.append(
            {
                "company_id": company_id,
                "sector": sector,
                "cfo_quality_score": cfo_quality_score,
                "cfo_quality_label": cfo_quality,
                "capex_intensity_pct": capex_intensity_pct,
                "capex_label": capex_label,
                "fcf_cagr_5yr": fcf_cagr,
                "fcf_conversion_pct": fcf_conversion_pct,
                "distress_flag": distress_flag,
                "deleveraging_flag": deleveraging_flag,
                "capital_allocation_label": capital_label,
            }
        )
       

    return pd.DataFrame(results)


def save_cashflow_intelligence():
    """
    Save Day 31 outputs.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    result = build_cashflow_intelligence()

    excel_path = (
        OUTPUT_DIR
        / "cashflow_intelligence.xlsx"
    )

    result.to_excel(
        excel_path,
        index=False,
    )

    # --------------------------------------------------------
    # DISTRESS ALERTS
    # --------------------------------------------------------

    distress = result[
        result["distress_flag"] == True
    ].copy()

    distress_path = (
        OUTPUT_DIR
        / "distress_alerts.csv"
    )

    distress.to_csv(
        distress_path,
        index=False,
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    print("=" * 60)
    print("DAY 31 - CASH FLOW INTELLIGENCE")
    print("=" * 60)

    print(
        f"Companies: {len(result)}"
    )

    print(
        f"Distress alerts: {len(distress)}"
    )

    print(
        f"Excel: {excel_path}"
    )

    print(
        f"CSV: {distress_path}"
    )

    print("=" * 60)

    required_columns = [
        "company_id",
        "cfo_quality_score",
        "cfo_quality_label",
        "capex_intensity_pct",
        "capex_label",
        "fcf_cagr_5yr",
        "fcf_conversion_pct",
        "distress_flag",
        "deleveraging_flag",
        "capital_allocation_label",
    ]

    missing = [
        col
        for col in required_columns
        if col not in result.columns
    ]

    if missing:
        print(
            "MISSING COLUMNS:",
            missing,
        )
    else:
        print(
            "SUCCESS: All required columns present."
        )

    print(
        f"Unique companies: "
        f"{result['company_id'].nunique()}"
    )

    print("=" * 60)

    return result


if __name__ == "__main__":
    save_cashflow_intelligence()