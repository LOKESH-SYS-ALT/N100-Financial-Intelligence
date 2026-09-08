import pytest

from src.analytics.cagr import (
    calculate_cagr,
    cagr_from_series,
    revenue_cagr_3yr,
    revenue_cagr_5yr,
    revenue_cagr_10yr,
    pat_cagr_3yr,
    pat_cagr_5yr,
    pat_cagr_10yr,
    eps_cagr_3yr,
    eps_cagr_5yr,
    eps_cagr_10yr,
    calculate_company_cagrs,
)


def test_normal_cagr():
    result, flag = calculate_cagr(100, 200, 5)

    assert result == pytest.approx(((200 / 100) ** (1 / 5) - 1) * 100)
    assert flag == "NORMAL"


def test_turnaround():
    result, flag = calculate_cagr(-100, 200, 5)

    assert result is None
    assert flag == "TURNAROUND"


def test_decline_to_loss():
    result, flag = calculate_cagr(100, -50, 5)

    assert result is None
    assert flag == "DECLINE_TO_LOSS"


def test_both_negative():
    result, flag = calculate_cagr(-100, -200, 5)

    assert result is None
    assert flag == "BOTH_NEGATIVE"


def test_zero_base():
    result, flag = calculate_cagr(0, 200, 5)

    assert result is None
    assert flag == "ZERO_BASE"


def test_insufficient_data():
    result, flag = cagr_from_series(
        [100, 110, 120],
        5,
    )

    assert result is None
    assert flag == "INSUFFICIENT"


def test_revenue_cagr_windows():
    values = [
        100,
        110,
        121,
        133.1,
        146.41,
        161.051,
        177.1561,
        194.87171,
        214.358881,
        235.7947691,
        259.37424601,
    ]

    result_3, flag_3 = revenue_cagr_3yr(values)
    result_5, flag_5 = revenue_cagr_5yr(values)
    result_10, flag_10 = revenue_cagr_10yr(values)

    assert result_3 == pytest.approx(10.0, abs=0.01)
    assert result_5 == pytest.approx(10.0, abs=0.01)
    assert result_10 == pytest.approx(10.0, abs=0.01)

    assert flag_3 == "NORMAL"
    assert flag_5 == "NORMAL"
    assert flag_10 == "NORMAL"


def test_pat_cagr():
    values = [100, 110, 121, 133.1, 146.41, 161.051]

    result, flag = pat_cagr_5yr(values)

    assert result == pytest.approx(10.0, abs=0.01)
    assert flag == "NORMAL"


def test_eps_cagr():
    values = [20, 22, 24.2, 26.62, 29.282, 32.2102]

    result, flag = eps_cagr_5yr(values)

    assert result == pytest.approx(10.0, abs=0.01)
    assert flag == "NORMAL"


def test_company_cagrs():
    revenue = [100, 110, 121, 133.1, 146.41, 161.051]
    pat = [50, 55, 60.5, 66.55, 73.205, 80.5255]
    eps = [10, 11, 12.1, 13.31, 14.641, 16.1051]

    result = calculate_company_cagrs(
        revenue,
        pat,
        eps,
    )

    assert result["revenue_cagr_5yr"] == pytest.approx(
        10.0,
        abs=0.01,
    )

    assert result["pat_cagr_5yr"] == pytest.approx(
        10.0,
        abs=0.01,
    )

    assert result["eps_cagr_5yr"] == pytest.approx(
        10.0,
        abs=0.01,
    )

    assert result["revenue_cagr_5yr_flag"] == "NORMAL"
    assert result["pat_cagr_5yr_flag"] == "NORMAL"
    assert result["eps_cagr_5yr_flag"] == "NORMAL"


def test_all_three_cagr_10yr_insufficient():
    values = [100, 110, 121, 133.1, 146.41, 161.051]

    revenue_result, revenue_flag = revenue_cagr_10yr(values)
    pat_result, pat_flag = pat_cagr_10yr(values)
    eps_result, eps_flag = eps_cagr_10yr(values)

    assert revenue_result is None
    assert pat_result is None
    assert eps_result is None

    assert revenue_flag == "INSUFFICIENT"
    assert pat_flag == "INSUFFICIENT"
    assert eps_flag == "INSUFFICIENT"
