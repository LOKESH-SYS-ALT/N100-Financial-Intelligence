import pandas as pd

from src.etl.validator import (
    clean_company_id,
    clean_year,
    validate_required_columns,
    validate_duplicates,
    validate_company_references,
    validate_null_company_ids,
    validate_opm,
    validate_sales,
    validate_all_datasets,
    save_report,
)


def base_data():
    return {
        "companies": pd.DataFrame(
            {
                "id": ["ABB", "TCS"],
                "company_name": ["Abbott India Ltd", "Tata Consultancy Services Ltd"],
            }
        ),
        "profitandloss": pd.DataFrame(
            {
                "id": [1, 2],
                "company_id": ["ABB", "TCS"],
                "year": ["Mar 2024", "Mar 2024"],
                "sales": [1000, 2000],
                "operating_profit": [200, 400],
                "opm_percentage": [20, 20],
            }
        ),
        "balancesheet": pd.DataFrame(
            {
                "id": [1],
                "company_id": ["ABB"],
                "year": ["Mar 2024"],
            }
        ),
        "cashflow": pd.DataFrame(
            {
                "id": [1],
                "company_id": ["ABB"],
                "year": ["Mar 2024"],
            }
        ),
        "analysis": pd.DataFrame(
            {
                "id": [1],
                "company_id": ["ABB"],
            }
        ),
        "documents": pd.DataFrame(
            {
                "id": [1],
                "company_id": ["ABB"],
            }
        ),
        "prosandcons": pd.DataFrame(
            {
                "id": [1],
                "company_id": ["ABB"],
            }
        ),
        "financial_ratios": pd.DataFrame(
            {
                "id": [1],
                "company_id": ["ABB"],
                "year": ["Mar 2024"],
            }
        ),
        "market_cap": pd.DataFrame(
            {
                "id": [1],
                "company_id": ["ABB"],
                "year": ["Mar 2024"],
            }
        ),
        "peer_groups": pd.DataFrame(
            {
                "id": [1],
                "company_id": ["ABB"],
            }
        ),
        "sectors": pd.DataFrame(
            {
                "id": [1],
                "company_id": ["ABB"],
            }
        ),
        "stock_prices": pd.DataFrame(
            {
                "id": [1],
                "company_id": ["ABB"],
                "date": ["2024-03-31"],
            }
        ),
    }


def test_clean_company_id_normalizes_value():
    assert clean_company_id(" abb ") == "ABB"


def test_clean_company_id_handles_null():
    assert clean_company_id(None) is None


def test_clean_company_id_handles_blank():
    assert clean_company_id("   ") is None


def test_clean_year_normalizes_value():
    assert clean_year(" Mar 2024 ") == "MAR 2024"


def test_clean_year_handles_null():
    assert clean_year(None) is None


def test_required_columns_pass():
    failures = validate_required_columns(base_data())
    assert failures == []


def test_required_columns_detects_missing_column():
    data = base_data()
    data["companies"] = data["companies"].drop(columns=["company_name"])

    failures = validate_required_columns(data)

    assert len(failures) == 1
    assert failures[0]["rule"] == "DQ-01"
    assert failures[0]["severity"] == "CRITICAL"


def test_duplicate_company_year_detected():
    data = base_data()
    data["profitandloss"] = pd.concat(
        [data["profitandloss"], data["profitandloss"].iloc[[0]]],
        ignore_index=True,
    )

    failures = validate_duplicates(data)

    assert len(failures) == 1
    assert failures[0]["rule"] == "DQ-02"
    assert failures[0]["company_id"] == "ABB"


def test_company_reference_detected():
    data = base_data()
    data["profitandloss"].loc[0, "company_id"] = "UNKNOWN"

    failures = validate_company_references(data)

    assert len(failures) == 1
    assert failures[0]["rule"] == "DQ-03"
    assert failures[0]["company_id"] == "UNKNOWN"


def test_null_company_id_detected():
    data = base_data()
    data["profitandloss"].loc[0, "company_id"] = None

    failures = validate_null_company_ids(data)

    assert len(failures) == 1
    assert failures[0]["rule"] == "DQ-04"


def test_opm_validation_passes():
    failures = validate_opm(base_data())
    assert failures == []


def test_opm_validation_detects_mismatch():
    data = base_data()
    data["profitandloss"].loc[0, "opm_percentage"] = 15

    failures = validate_opm(data)

    assert len(failures) == 1
    assert failures[0]["rule"] == "DQ-05"
    assert failures[0]["severity"] == "WARNING"


def test_sales_validation_passes():
    failures = validate_sales(base_data())
    assert failures == []


def test_sales_validation_detects_non_positive():
    data = base_data()
    data["profitandloss"].loc[0, "sales"] = 0

    failures = validate_sales(data)

    assert len(failures) == 1
    assert failures[0]["rule"] == "DQ-06"
    assert failures[0]["severity"] == "WARNING"


def test_validate_all_datasets_clean():
    failures = validate_all_datasets(base_data())
    assert failures == []


def test_save_report_creates_csv():
    failures = [
        {
            "rule": "DQ-06",
            "dataset": "profitandloss",
            "severity": "WARNING",
            "company_id": "ABB",
            "year": "MAR 2024",
            "message": "Sales is zero or negative",
        }
    ]

    report_path = save_report(failures)

    assert report_path.exists()
    assert report_path.name == "validation_failures.csv"
