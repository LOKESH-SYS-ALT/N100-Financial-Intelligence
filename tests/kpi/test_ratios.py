"""
Sprint 2 - Day 08
Profitability Ratio Tests
"""

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    opm_cross_check,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    profitability_ratios,
)


def test_net_profit_margin_normal():
    assert net_profit_margin(200, 1000) == 20.0


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(200, 0) is None


def test_operating_profit_margin_normal():
    assert operating_profit_margin(150, 1000) == 15.0


def test_opm_cross_check_match():
    result = opm_cross_check(15.0, 15.0)

    assert result["mismatch"] is False
    assert result["difference"] == 0


def test_opm_cross_check_mismatch():
    result = opm_cross_check(15.0, 17.0)

    assert result["mismatch"] is True
    assert result["difference"] == 2.0


def test_roe_normal():
    assert (
        return_on_equity(
            200,
            500,
            500,
        )
        == 20.0
    )


def test_roe_negative_equity():
    assert (
        return_on_equity(
            200,
            -600,
            500,
        )
        is None
    )


def test_roce_normal():
    assert (
        return_on_capital_employed(
            200,
            500,
            500,
            1000,
        )
        == 10.0
    )


def test_roa_zero_assets():
    assert (
        return_on_assets(
            200,
            0,
        )
        is None
    )


def test_profitability_ratios_integration():
    result = profitability_ratios(
        net_profit=200,
        sales=1000,
        operating_profit=150,
        equity_capital=500,
        reserves=500,
        ebit=200,
        borrowings=1000,
        total_assets=2000,
        source_opm=15.0,
    )

    assert result["net_profit_margin_pct"] == 20.0
    assert result["operating_profit_margin_pct"] == 15.0
    assert result["return_on_equity_pct"] == 20.0
    assert result["return_on_capital_employed_pct"] == 10.0
    assert result["return_on_assets_pct"] == 10.0
    assert result["opm_mismatch_flag"] is False
