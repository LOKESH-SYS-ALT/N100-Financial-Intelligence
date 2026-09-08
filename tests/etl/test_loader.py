import pandas as pd
import pytest

from src.etl.loader import (
    DATASETS,
    HEADER_ROW_1_FILES,
    UNIQUE_COMPANY_YEAR_FILES,
    load_excel,
    load_all_datasets,
    print_dataset_summary,
)


def test_datasets_contains_12_entries():
    assert len(DATASETS) == 12


def test_dataset_filenames_are_xlsx():
    assert all(filename.endswith(".xlsx") for filename in DATASETS.values())


def test_header_row_configuration():
    assert "companies.xlsx" in HEADER_ROW_1_FILES
    assert "profitandloss.xlsx" in HEADER_ROW_1_FILES
    assert "financial_ratios.xlsx" not in HEADER_ROW_1_FILES


def test_unique_company_year_configuration():
    assert "profitandloss.xlsx" in UNIQUE_COMPANY_YEAR_FILES
    assert "balancesheet.xlsx" in UNIQUE_COMPANY_YEAR_FILES
    assert "cashflow.xlsx" in UNIQUE_COMPANY_YEAR_FILES
    assert "financial_ratios.xlsx" in UNIQUE_COMPANY_YEAR_FILES


def test_load_excel_missing_file():
    with pytest.raises(FileNotFoundError):
        load_excel("__definitely_missing__.xlsx")


def test_load_excel_returns_dataframe():
    df = load_excel("companies.xlsx")
    assert isinstance(df, pd.DataFrame)


def test_load_excel_removes_empty_rows():
    df = load_excel("companies.xlsx")
    assert not df.isna().all(axis=1).any()


def test_load_excel_has_clean_column_names():
    df = load_excel("companies.xlsx")
    assert all(str(column) == str(column).strip() for column in df.columns)


def test_load_all_datasets_returns_12_datasets():
    data = load_all_datasets()

    assert isinstance(data, dict)
    assert len(data) == 12
    assert set(data.keys()) == set(DATASETS.keys())


def test_print_dataset_summary(capsys):
    data = {
        "companies": pd.DataFrame({"company_id": ["ABB", "TCS"]}),
        "sectors": pd.DataFrame({"company_id": ["ABB", "TCS"]}),
    }

    print_dataset_summary(data)

    output = capsys.readouterr().out

    assert "N100 FINANCIAL INTELLIGENCE - DATASET SUMMARY" in output
    assert "companies" in output
    assert "sectors" in output
    assert "Total datasets loaded : 2" in output
