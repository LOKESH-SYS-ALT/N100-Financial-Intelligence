"""
N100 Financial Intelligence
Sprint 2 - CAGR Engine

Day 10:
- Revenue CAGR
- PAT CAGR
- EPS CAGR
- 3-year / 5-year / 10-year windows
- Six CAGR edge cases
"""

from typing import Optional, Sequence

# ============================================================
# CAGR EDGE-CASE FLAGS
# ============================================================

POSITIVE_TO_POSITIVE = "NORMAL"
DECLINE_TO_LOSS = "DECLINE_TO_LOSS"
TURNAROUND = "TURNAROUND"
BOTH_NEGATIVE = "BOTH_NEGATIVE"
ZERO_BASE = "ZERO_BASE"
INSUFFICIENT = "INSUFFICIENT"


# ============================================================
# CORE CAGR
# ============================================================


def calculate_cagr(
    start_value: float,
    end_value: float,
    years: int,
) -> tuple[Optional[float], str]:
    """
    Calculate CAGR with all required edge cases.

    Formula:
        ((end / start) ** (1 / years) - 1) * 100

    Returns:
        (cagr_value, flag)
    """

    if years <= 0:
        raise ValueError("years must be greater than zero")

    # Zero base
    if start_value == 0:
        return None, ZERO_BASE

    # Positive -> positive
    if start_value > 0 and end_value > 0:
        cagr = ((end_value / start_value) ** (1 / years) - 1) * 100
        return cagr, POSITIVE_TO_POSITIVE

    # Positive -> negative
    if start_value > 0 and end_value < 0:
        return None, DECLINE_TO_LOSS

    # Negative -> positive
    if start_value < 0 and end_value > 0:
        return None, TURNAROUND

    # Negative -> negative
    if start_value < 0 and end_value < 0:
        return None, BOTH_NEGATIVE

    # Any remaining zero-end case
    if end_value == 0:
        return None, DECLINE_TO_LOSS

    return None, INSUFFICIENT


# ============================================================
# WINDOW / SERIES HELPERS
# ============================================================


def _normalise_series(
    values: Sequence[float],
) -> list[float]:
    """Convert a sequence to a clean numeric list."""

    return [float(value) for value in values if value is not None]


def cagr_from_series(
    values: Sequence[float],
    years: int,
) -> tuple[Optional[float], str]:
    """
    Calculate CAGR from an ordered historical series.

    The series must contain at least years + 1 observations.

    Example:
        5-year CAGR requires 6 annual observations:
        Year 0 -> Year 1 -> ... -> Year 5
    """

    clean_values = _normalise_series(values)

    required_points = years + 1

    if len(clean_values) < required_points:
        return None, INSUFFICIENT

    start_value = clean_values[-required_points]
    end_value = clean_values[-1]

    return calculate_cagr(
        start_value,
        end_value,
        years,
    )


def cagr_window(
    values: Sequence[float],
    window_years: int,
) -> tuple[Optional[float], str]:
    """
    Alias/helper for calculating a specific CAGR window.
    """

    return cagr_from_series(
        values,
        window_years,
    )


# ============================================================
# INDIVIDUAL WINDOW FUNCTIONS
# ============================================================


def revenue_cagr_3yr(
    revenue_values: Sequence[float],
) -> tuple[Optional[float], str]:
    """Calculate 3-year Revenue CAGR."""
    return cagr_from_series(revenue_values, 3)


def revenue_cagr_5yr(
    revenue_values: Sequence[float],
) -> tuple[Optional[float], str]:
    """Calculate 5-year Revenue CAGR."""
    return cagr_from_series(revenue_values, 5)


def revenue_cagr_10yr(
    revenue_values: Sequence[float],
) -> tuple[Optional[float], str]:
    """Calculate 10-year Revenue CAGR."""
    return cagr_from_series(revenue_values, 10)


def pat_cagr_3yr(
    pat_values: Sequence[float],
) -> tuple[Optional[float], str]:
    """Calculate 3-year PAT CAGR."""
    return cagr_from_series(pat_values, 3)


def pat_cagr_5yr(
    pat_values: Sequence[float],
) -> tuple[Optional[float], str]:
    """Calculate 5-year PAT CAGR."""
    return cagr_from_series(pat_values, 5)


def pat_cagr_10yr(
    pat_values: Sequence[float],
) -> tuple[Optional[float], str]:
    """Calculate 10-year PAT CAGR."""
    return cagr_from_series(pat_values, 10)


def eps_cagr_3yr(
    eps_values: Sequence[float],
) -> tuple[Optional[float], str]:
    """Calculate 3-year EPS CAGR."""
    return cagr_from_series(eps_values, 3)


def eps_cagr_5yr(
    eps_values: Sequence[float],
) -> tuple[Optional[float], str]:
    """Calculate 5-year EPS CAGR."""
    return cagr_from_series(eps_values, 5)


def eps_cagr_10yr(
    eps_values: Sequence[float],
) -> tuple[Optional[float], str]:
    """Calculate 10-year EPS CAGR."""
    return cagr_from_series(eps_values, 10)


# ============================================================
# GENERIC METRIC ENGINE
# ============================================================


def calculate_metric_cagrs(
    values: Sequence[float],
) -> dict:
    """
    Calculate 3-year, 5-year and 10-year CAGR values
    for a generic metric.
    """

    cagr_3, flag_3 = cagr_from_series(values, 3)
    cagr_5, flag_5 = cagr_from_series(values, 5)
    cagr_10, flag_10 = cagr_from_series(values, 10)

    return {
        "cagr_3yr": cagr_3,
        "cagr_3yr_flag": flag_3,
        "cagr_5yr": cagr_5,
        "cagr_5yr_flag": flag_5,
        "cagr_10yr": cagr_10,
        "cagr_10yr_flag": flag_10,
    }


# ============================================================
# COMPLETE COMPANY CAGR ENGINE
# ============================================================


def calculate_company_cagrs(
    revenue_values: Sequence[float],
    pat_values: Sequence[float],
    eps_values: Sequence[float],
) -> dict:
    """
    Calculate all CAGR metrics required by Sprint 2.
    """

    revenue = calculate_metric_cagrs(revenue_values)
    pat = calculate_metric_cagrs(pat_values)
    eps = calculate_metric_cagrs(eps_values)

    return {
        # Revenue
        "revenue_cagr_3yr": revenue["cagr_3yr"],
        "revenue_cagr_3yr_flag": revenue["cagr_3yr_flag"],
        "revenue_cagr_5yr": revenue["cagr_5yr"],
        "revenue_cagr_5yr_flag": revenue["cagr_5yr_flag"],
        "revenue_cagr_10yr": revenue["cagr_10yr"],
        "revenue_cagr_10yr_flag": revenue["cagr_10yr_flag"],
        # PAT
        "pat_cagr_3yr": pat["cagr_3yr"],
        "pat_cagr_3yr_flag": pat["cagr_3yr_flag"],
        "pat_cagr_5yr": pat["cagr_5yr"],
        "pat_cagr_5yr_flag": pat["cagr_5yr_flag"],
        "pat_cagr_10yr": pat["cagr_10yr"],
        "pat_cagr_10yr_flag": pat["cagr_10yr_flag"],
        # EPS
        "eps_cagr_3yr": eps["cagr_3yr"],
        "eps_cagr_3yr_flag": eps["cagr_3yr_flag"],
        "eps_cagr_5yr": eps["cagr_5yr"],
        "eps_cagr_5yr_flag": eps["cagr_5yr_flag"],
        "eps_cagr_10yr": eps["cagr_10yr"],
        "eps_cagr_10yr_flag": eps["cagr_10yr_flag"],
    }


# ============================================================
# SIMPLE VALUE-BASED HELPERS
# ============================================================


def revenue_cagr(
    start_value: float,
    end_value: float,
    years: int,
) -> Optional[float]:
    """Return only the CAGR value."""
    value, _ = calculate_cagr(
        start_value,
        end_value,
        years,
    )
    return value


def pat_cagr(
    start_value: float,
    end_value: float,
    years: int,
) -> Optional[float]:
    """Return only the PAT CAGR value."""
    value, _ = calculate_cagr(
        start_value,
        end_value,
        years,
    )
    return value


def eps_cagr(
    start_value: float,
    end_value: float,
    years: int,
) -> Optional[float]:
    """Return only the EPS CAGR value."""
    value, _ = calculate_cagr(
        start_value,
        end_value,
        years,
    )
    return value


# ============================================================
# RESULT HELPER
# ============================================================


def cagr_result(
    start_value: float,
    end_value: float,
    years: int,
) -> dict:
    """
    Return CAGR and its edge-case flag as a dictionary.
    """

    value, flag = calculate_cagr(
        start_value,
        end_value,
        years,
    )

    return {
        "cagr": value,
        "flag": flag,
    }


# ============================================================
# MODULE SELF-CHECK
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("N100 FINANCIAL INTELLIGENCE - CAGR ENGINE")
    print("=" * 70)

    normal = calculate_cagr(
        100,
        200,
        5,
    )

    turnaround = calculate_cagr(
        -100,
        200,
        5,
    )

    decline = calculate_cagr(
        100,
        -50,
        5,
    )

    both_negative = calculate_cagr(
        -100,
        -200,
        5,
    )

    zero_base = calculate_cagr(
        0,
        200,
        5,
    )

    insufficient = cagr_from_series(
        [100, 110, 120],
        5,
    )

    print("Normal       :", normal)
    print("Turnaround   :", turnaround)
    print("Decline loss :", decline)
    print("Both negative:", both_negative)
    print("Zero base    :", zero_base)
    print("Insufficient :", insufficient)

    print("=" * 70)
