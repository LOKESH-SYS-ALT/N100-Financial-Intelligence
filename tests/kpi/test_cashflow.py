import pytest

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_pat_ratio,
    average_cfo_pat_ratio,
    cfo_quality_label,
    capex_intensity,
    capex_intensity_label,
    fcf_conversion_rate,
    cash_flow_sign,
    capital_allocation_pattern,
    calculate_cashflow_kpis,
)


def test_free_cash_flow():
    assert free_cash_flow(500, -200) == 300


def test_negative_free_cash_flow():
    assert free_cash_flow(100, -300) == -200


def test_cfo_pat_ratio():
    assert cfo_pat_ratio(150, 100) == pytest.approx(1.5)


def test_cfo_pat_zero_pat():
    assert cfo_pat_ratio(150, 0) is None


def test_average_cfo_pat_ratio():
    result = average_cfo_pat_ratio(
        [150, 120, 100],
        [100, 100, 100],
    )

    assert result == pytest.approx(1.2333333)


def test_cfo_quality_labels():
    assert cfo_quality_label(1.2) == "High Quality"
    assert cfo_quality_label(0.75) == "Moderate"
    assert cfo_quality_label(0.3) == "Accrual Risk"
    assert cfo_quality_label(None) is None


def test_capex_intensity():
    assert capex_intensity(-50, 1000) == pytest.approx(5.0)


def test_capex_zero_sales():
    assert capex_intensity(-50, 0) is None


def test_capex_labels():
    assert capex_intensity_label(2.5) == "Asset Light"
    assert capex_intensity_label(5.0) == "Moderate"
    assert capex_intensity_label(10.0) == "Capital Intensive"


def test_fcf_conversion():
    assert fcf_conversion_rate(200, 400) == pytest.approx(50.0)


def test_fcf_conversion_zero_op():
    assert fcf_conversion_rate(200, 0) is None


def test_cash_flow_sign():
    assert cash_flow_sign(100) == "+"
    assert cash_flow_sign(0) == "+"
    assert cash_flow_sign(-100) == "-"


def test_capital_allocation_reinvestor():
    assert (
        capital_allocation_pattern(
            100,
            -50,
            -25,
            0.8,
        )
        == "Reinvestor"
    )


def test_capital_allocation_shareholder_returns():
    assert (
        capital_allocation_pattern(
            200,
            -50,
            -25,
            1.5,
        )
        == "Shareholder Returns"
    )


def test_capital_allocation_mixed():
    assert (
        capital_allocation_pattern(
            100,
            -50,
            25,
        )
        == "Mixed"
    )


def test_capital_allocation_liquidating_assets():
    assert (
        capital_allocation_pattern(
            100,
            50,
            -25,
        )
        == "Liquidating Assets"
    )


def test_capital_allocation_distress():
    assert (
        capital_allocation_pattern(
            -100,
            50,
            25,
        )
        == "Distress Signal"
    )


def test_capital_allocation_growth_debt():
    assert (
        capital_allocation_pattern(
            -100,
            -50,
            100,
        )
        == "Growth Funded by Debt"
    )


def test_capital_allocation_cash_accumulator():
    assert (
        capital_allocation_pattern(
            100,
            50,
            25,
        )
        == "Cash Accumulator"
    )


def test_capital_allocation_pre_revenue():
    assert (
        capital_allocation_pattern(
            -100,
            -50,
            -25,
        )
        == "Pre-Revenue"
    )


def test_cashflow_kpi_integration():
    result = calculate_cashflow_kpis(
        operating_activity=500,
        investing_activity=-200,
        financing_activity=-100,
        sales=2000,
        operating_profit=400,
        cfo_pat_ratio_value=1.25,
    )

    assert result["free_cash_flow_cr"] == 300
    assert result["cfo_pat_ratio"] == 1.25
    assert result["cfo_quality_label"] == "High Quality"
    assert result["capex_intensity_pct"] == pytest.approx(10.0)
    assert result["capex_intensity_label"] == "Capital Intensive"
    assert result["fcf_conversion_rate_pct"] == pytest.approx(75.0)
    assert result["capital_allocation_pattern"] == "Shareholder Returns"
