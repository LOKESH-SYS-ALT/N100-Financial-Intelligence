import pytest

from src.analytics.ratios import (
    debt_to_equity,
    interest_coverage,
    net_debt,
    asset_turnover,
    high_leverage_flag,
    icr_warning_flag,
    icr_label,
)


def test_debt_to_equity_normal():
    assert debt_to_equity(200, 1000) == pytest.approx(0.2)


def test_debt_to_equity_debt_free():
    assert debt_to_equity(0, 1000) == 0


def test_debt_to_equity_negative_equity():
    assert debt_to_equity(200, -100) is None


def test_interest_coverage_normal():
    assert interest_coverage(300, 50) == pytest.approx(6.0)


def test_interest_coverage_zero_interest():
    assert interest_coverage(300, 0) is None


def test_icr_label_debt_free():
    assert icr_label(None) == "Debt Free"


def test_high_debt_to_equity_flag():
    assert high_leverage_flag(6.0, "Industrial") is True


def test_financials_high_leverage_suppressed():
    assert high_leverage_flag(6.0, "Financials") is False
