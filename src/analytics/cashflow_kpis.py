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