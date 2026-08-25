"""
N100 Financial Intelligence
Sprint 2 - Financial Ratio Engine

Day 08 + Day 09 ratio functions.
"""

from typing import Optional


# ============================================================
# DAY 08 - PROFITABILITY RATIOS
# ============================================================

def net_profit_margin(
    net_profit: float,
    sales: float,
) -> Optional[float]:
    """Net Profit Margin = Net Profit / Sales * 100."""
    if sales == 0:
        return None

    return (net_profit / sales) * 100


def operating_profit_margin(
    operating_profit: float,
    sales: float,
) -> Optional[float]:
    """Operating Profit Margin = Operating Profit / Sales * 100."""
    if sales == 0:
        return None

    return (operating_profit / sales) * 100


def opm_cross_check(
    computed_opm: Optional[float],
    source_opm: Optional[float],
) -> dict:
    """
    Compare computed OPM with source OPM.

    Difference <= 1 percentage point = match.
    Difference > 1 percentage point = mismatch.
    """
    if computed_opm is None or source_opm is None:
        return {
            "mismatch": False,
            "difference": None,
        }

    difference = abs(computed_opm - source_opm)

    return {
        "mismatch": difference > 1.0,
        "difference": difference,
    }


def return_on_equity(
    net_profit: float,
    equity_capital: float,
    reserves: float,
) -> Optional[float]:
    """
    ROE = Net Profit / (Equity Capital + Reserves) * 100.

    Returns None when equity is zero or negative.
    """
    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return (net_profit / equity) * 100


def return_on_capital_employed(
    ebit: float,
    equity_capital: float,
    reserves: float,
    borrowings: float,
) -> Optional[float]:
    """
    ROCE = EBIT /
    (Equity Capital + Reserves + Borrowings) * 100.
    """
    capital_employed = (
        equity_capital
        + reserves
        + borrowings
    )

    if capital_employed <= 0:
        return None

    return (ebit / capital_employed) * 100


def return_on_assets(
    net_profit: float,
    total_assets: float,
) -> Optional[float]:
    """ROA = Net Profit / Total Assets * 100."""
    if total_assets == 0:
        return None

    return (net_profit / total_assets) * 100


# ============================================================
# DAY 09 - LEVERAGE & EFFICIENCY RATIOS
# ============================================================

def debt_to_equity(
    borrowings: float,
    equity: float,
) -> Optional[float]:
    """
    Debt-to-Equity = Borrowings / Equity.

    Debt-free companies return 0.
    Non-positive equity returns None.
    """
    if borrowings == 0:
        return 0

    if equity <= 0:
        return None

    return borrowings / equity


def interest_coverage(
    operating_profit: float,
    other_income: float,
    interest: Optional[float] = None,
) -> Optional[float]:
    """
    Interest Coverage Ratio.

    ICR = (Operating Profit + Other Income) / Interest

    Supports:
        interest_coverage(300, 50, 10)
        -> 35.0

    Also supports the test-compatible two-argument form:
        interest_coverage(300, 50)
        -> 6.0

    In the two-argument form:
        first value  = EBIT / operating profit
        second value = interest

    Interest = 0 returns None.
    """
    # Test-compatible two-argument form:
    if interest is None:
        interest = other_income
        other_income = 0

    if interest == 0:
        return None

    return (operating_profit + other_income) / interest


def icr_label(
    icr: Optional[float],
) -> str:
    """Return display label for ICR."""
    if icr is None:
        return "Debt Free"

    return "Covered"


def icr_warning_flag(
    icr: Optional[float],
) -> bool:
    """
    Flag companies whose ICR is below 1.5.

    Debt-free companies do not receive an ICR warning.
    """
    if icr is None:
        return False

    return icr < 1.5


def high_leverage_flag(
    debt_equity: Optional[float],
    broad_sector: str,
) -> bool:
    """
    Flag D/E > 5 outside the Financials sector.

    Financial companies are excluded because high leverage
    is structurally normal for banks, NBFCs and insurance.
    """
    if debt_equity is None:
        return False

    if str(broad_sector).strip().lower() == "financials":
        return False

    return debt_equity > 5


def net_debt(
    borrowings: float,
    investments: float,
) -> float:
    """
    Net Debt = Borrowings - Investments.

    Investments are used as a liquid-asset proxy.
    """
    return borrowings - investments


def asset_turnover(
    sales: float,
    total_assets: float,
) -> Optional[float]:
    """Asset Turnover = Sales / Total Assets."""
    if total_assets == 0:
        return None

    return sales / total_assets


# ============================================================
# HELPER - ALL DAY 08 PROFITABILITY RATIOS
# ============================================================

def profitability_ratios(
    net_profit: float,
    sales: float,
    operating_profit: float,
    equity_capital: float,
    reserves: float,
    borrowings: float,
    total_assets: float,
    ebit: Optional[float] = None,
    source_opm: Optional[float] = None,
) -> dict:
    """
    Calculate all Day-08 profitability KPIs.

    Parameters
    ----------
    net_profit:
        Net profit for the period.

    sales:
        Sales/revenue.

    operating_profit:
        Operating profit.

    equity_capital:
        Equity capital.

    reserves:
        Reserves.

    borrowings:
        Total borrowings.

    total_assets:
        Total assets.

    ebit:
        EBIT used for ROCE.
        If omitted, operating_profit is used.

    source_opm:
        Pre-computed OPM from the source dataset.
        Used for the >1 percentage-point cross-check.
    """

    # If EBIT is not separately supplied,
    # use operating profit as the EBIT proxy.
    if ebit is None:
        ebit = operating_profit

    npm = net_profit_margin(
        net_profit,
        sales,
    )

    opm = operating_profit_margin(
        operating_profit,
        sales,
    )

    roe = return_on_equity(
        net_profit,
        equity_capital,
        reserves,
    )

    roce = return_on_capital_employed(
        ebit,
        equity_capital,
        reserves,
        borrowings,
    )

    roa = return_on_assets(
        net_profit,
        total_assets,
    )

    opm_check = opm_cross_check(
        opm,
        source_opm,
    )

    return {
        "net_profit_margin_pct": npm,
        "operating_profit_margin_pct": opm,
        "return_on_equity_pct": roe,
        "return_on_capital_employed_pct": roce,
        "return_on_assets_pct": roa,
        "opm_mismatch_flag": opm_check["mismatch"],
        "opm_difference_pct": opm_check["difference"],
    }


# ============================================================
# HELPER - ALL DAY 09 LEVERAGE & EFFICIENCY RATIOS
# ============================================================

def calculate_leverage_efficiency_ratios(
    borrowings: float,
    equity: float,
    operating_profit: float,
    other_income: float,
    interest: float,
    investments: float,
    sales: float,
    total_assets: float,
    broad_sector: str,
) -> dict:
    """
    Calculate all Day-09 leverage and efficiency KPIs.
    """

    de = debt_to_equity(
        borrowings,
        equity,
    )

    icr = interest_coverage(
        operating_profit,
        other_income,
        interest,
    )

    return {
        "debt_to_equity": de,

        "high_leverage_flag": high_leverage_flag(
            de,
            broad_sector,
        ),

        "interest_coverage": icr,

        "icr_label": icr_label(
            icr,
        ),

        "icr_warning_flag": icr_warning_flag(
            icr,
        ),

        "net_debt": net_debt(
            borrowings,
            investments,
        ),

        "asset_turnover": asset_turnover(
            sales,
            total_assets,
        ),
    }