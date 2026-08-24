import pandas as pd

from src.etl.normalizer import (
    normalize_columns,
    normalize_date,
    normalize_numeric,
    normalize_ticker,
    normalize_year,
)


# ============================================================
# normalize_year() — 20 TESTS
# ============================================================

def test_normalize_year_integer():
    assert normalize_year(2024) == 2024


def test_normalize_year_float():
    assert normalize_year(2024.0) == 2024


def test_normalize_year_string():
    assert normalize_year("2024") == 2024


def test_normalize_year_fy_prefix():
    assert normalize_year("FY2024") == 2024


def test_normalize_year_fy_lowercase():
    assert normalize_year("fy2024") == 2024


def test_normalize_year_financial_year():
    assert normalize_year("2024-25") == 2024


def test_normalize_year_financial_year_reverse():
    assert normalize_year("FY 2024-25") == 2024


def test_normalize_year_with_spaces():
    assert normalize_year(" 2024 ") == 2024


def test_normalize_year_text_prefix():
    assert normalize_year("Year 2024") == 2024


def test_normalize_year_text_suffix():
    assert normalize_year("2024 Annual") == 2024


def test_normalize_year_2019():
    assert normalize_year("FY2019") == 2019


def test_normalize_year_2000():
    assert normalize_year("2000") == 2000


def test_normalize_year_1999():
    assert normalize_year("1999") == 1999


def test_normalize_year_none():
    assert normalize_year(None) is None


def test_normalize_year_nan():
    assert normalize_year(float("nan")) is None


def test_normalize_year_invalid_text():
    assert normalize_year("unknown") is None


def test_normalize_year_empty_string():
    assert normalize_year("") is None


def test_normalize_year_whitespace():
    assert normalize_year("   ") is None


def test_normalize_year_embedded_year():
    assert normalize_year("Annual Report 2023") == 2023


def test_normalize_year_multiple_years():
    assert normalize_year("2023-24 / 2024-25") == 2023


# ============================================================
# normalize_ticker() — 15 TESTS
# ============================================================

def test_normalize_ticker_uppercase():
    assert normalize_ticker("tcs") == "TCS"


def test_normalize_ticker_already_uppercase():
    assert normalize_ticker("TCS") == "TCS"


def test_normalize_ticker_spaces():
    assert normalize_ticker(" TCS ") == "TCS"


def test_normalize_ticker_nse_suffix():
    assert normalize_ticker("TCS.NS") == "TCS"


def test_normalize_ticker_bse_suffix():
    assert normalize_ticker("TCS.BO") == "TCS"


def test_normalize_ticker_lowercase_nse():
    assert normalize_ticker("tcs.ns") == "TCS"


def test_normalize_ticker_lowercase_bse():
    assert normalize_ticker("tcs.bo") == "TCS"


def test_normalize_ticker_spaces_with_suffix():
    assert normalize_ticker(" TCS.NS ") == "TCS"


def test_normalize_ticker_adani():
    assert normalize_ticker("ADANIENT") == "ADANIENT"


def test_normalize_ticker_reliance():
    assert normalize_ticker("reliance") == "RELIANCE"


def test_normalize_ticker_infosis():
    assert normalize_ticker("infosys") == "INFOSYS"


def test_normalize_ticker_none():
    assert normalize_ticker(None) is None


def test_normalize_ticker_nan():
    assert normalize_ticker(float("nan")) is None


def test_normalize_ticker_empty():
    assert normalize_ticker("") == ""


def test_normalize_ticker_numeric():
    assert normalize_ticker(123) == "123"


# ============================================================
# normalize_columns() — 3 TESTS
# ============================================================

def test_normalize_columns_spaces():
    df = pd.DataFrame(columns=[" Company Name "])

    result = normalize_columns(df)

    assert list(result.columns) == ["company_name"]


def test_normalize_columns_special_characters():
    df = pd.DataFrame(columns=["Book Value (%)"])

    result = normalize_columns(df)

    assert list(result.columns) == ["book_value"]


def test_normalize_columns_lowercase():
    df = pd.DataFrame(columns=["Company_ID", "YEAR"])

    result = normalize_columns(df)

    assert list(result.columns) == ["company_id", "year"]


# ============================================================
# normalize_numeric() — 2 TESTS
# ============================================================

def test_normalize_numeric():
    df = pd.DataFrame({
        "sales": ["100", "200", "300"]
    })

    result = normalize_numeric(df, ["sales"])

    assert result["sales"].tolist() == [100, 200, 300]


def test_normalize_numeric_invalid_value():
    df = pd.DataFrame({
        "sales": ["100", "invalid", "300"]
    })

    result = normalize_numeric(df, ["sales"])

    assert result["sales"].iloc[0] == 100
    assert pd.isna(result["sales"].iloc[1])
    assert result["sales"].iloc[2] == 300


# ============================================================
# normalize_date() — 2 TESTS
# ============================================================

def test_normalize_date():
    df = pd.DataFrame({
        "date": ["2020-01-01", "2021-01-01"]
    })

    result = normalize_date(df)

    assert pd.api.types.is_datetime64_any_dtype(result["date"])


def test_normalize_date_invalid_value():
    df = pd.DataFrame({
        "date": ["2020-01-01", "invalid"]
    })

    result = normalize_date(df)

    assert pd.notna(result["date"].iloc[0])
    assert pd.isna(result["date"].iloc[1])