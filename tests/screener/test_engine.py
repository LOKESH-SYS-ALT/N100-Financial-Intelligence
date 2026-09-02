import pandas as pd
import pytest

from src.screener.engine import (
    apply_filters,
    calculate_composite_quality_score,
    run_preset,
)


def make_test_dataframe():
    return pd.DataFrame(
        {
            "company_id": ["AAA", "BBB", "CCC"],
            "return_on_equity_pct": [20.0, 10.0, 5.0],
            "return_on_capital_employed_pct": [18.0, 9.0, 4.0],
            "net_profit_margin_pct": [15.0, 8.0, 3.0],
            "free_cash_flow_cr": [500.0, 100.0, -50.0],
            "cash_from_operations_cr": [600.0, 150.0, -20.0],
            "revenue_cagr_5yr": [15.0, 8.0, 2.0],
            "pat_cagr_5yr": [18.0, 7.0, 1.0],
            "debt_to_equity": [0.2, 1.0, 2.0],
            "interest_coverage": [10.0, 4.0, 1.5],
            "sales": [10000.0, 6000.0, 3000.0],
            "market_cap_cr": [100000.0, 50000.0, 10000.0],
            "broad_sector": ["Technology", "Industrials", "Industrials"],
        }
    )


def test_composite_quality_score_has_no_nan():
    df = make_test_dataframe()

    result = calculate_composite_quality_score(df)

    assert "composite_quality_score" in result.columns
    assert result["composite_quality_score"].notna().all()


def test_composite_quality_score_is_between_zero_and_hundred():
    df = make_test_dataframe()

    result = calculate_composite_quality_score(df)

    assert (result["composite_quality_score"] >= 0).all()
    assert (result["composite_quality_score"] <= 100).all()


def test_roe_filter():
    df = make_test_dataframe()

    result = apply_filters(
        df,
        {"roe_min": 15},
    )

    assert set(result["company_id"]) == {"AAA"}


def test_debt_to_equity_filter():
    df = make_test_dataframe()

    result = apply_filters(
        df,
        {"debt_to_equity_max": 1.0},
    )

    assert set(result["company_id"]) == {"AAA", "BBB"}


def test_sales_filter():
    df = make_test_dataframe()

    result = apply_filters(
        df,
        {"sales_min": 5000},
    )

    assert set(result["company_id"]) == {"AAA", "BBB"}


def test_multiple_filters():
    df = make_test_dataframe()

    result = apply_filters(
        df,
        {
            "roe_min": 10,
            "debt_to_equity_max": 1.0,
        },
    )

    assert set(result["company_id"]) == {"AAA", "BBB"}


def test_filter_results_are_sorted_by_composite_score():
    df = make_test_dataframe()

    result = apply_filters(df)

    scores = result["composite_quality_score"].tolist()

    assert scores == sorted(
        scores,
        reverse=True,
    )


@pytest.mark.parametrize(
    "preset_name",
    [
        "quality_compounder",
        "value_pick",
        "growth_accelerator",
        "dividend_champion",
        "debt_free_blue_chip",
        "turnaround_watch",
    ],
)
def test_all_presets_run(preset_name):
    result = run_preset(preset_name)

    assert isinstance(result, pd.DataFrame)
    assert "company_id" in result.columns
    assert "composite_quality_score" in result.columns
    assert result["composite_quality_score"].notna().all()