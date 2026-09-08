from pathlib import Path

import pandas as pd

from src.etl.loader import load_all_datasets

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

YEAR_KEY_DATASETS = {
    "profitandloss",
    "balancesheet",
    "cashflow",
    "financial_ratios",
    "market_cap",
}

COMPANY_REFERENCE_DATASETS = {
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons",
    "financial_ratios",
    "market_cap",
    "peer_groups",
    "sectors",
    "stock_prices",
}


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------


def clean_company_id(value):
    if pd.isna(value):
        return None

    value = str(value).strip().upper()

    if not value:
        return None

    return value


def clean_year(value):
    if pd.isna(value):
        return None

    return str(value).strip().upper()


# ---------------------------------------------------------
# DQ-01: Required columns
# ---------------------------------------------------------


def validate_required_columns(data):
    failures = []

    required_columns = {
        "companies": [
            "id",
            "company_name",
        ],
        "profitandloss": [
            "id",
            "company_id",
            "year",
            "sales",
            "operating_profit",
            "opm_percentage",
        ],
        "balancesheet": [
            "id",
            "company_id",
            "year",
        ],
        "cashflow": [
            "id",
            "company_id",
            "year",
        ],
        "analysis": [
            "id",
            "company_id",
        ],
        "documents": [
            "id",
            "company_id",
        ],
        "prosandcons": [
            "id",
            "company_id",
        ],
        "financial_ratios": [
            "id",
            "company_id",
            "year",
        ],
        "market_cap": [
            "id",
            "company_id",
            "year",
        ],
        "peer_groups": [
            "id",
            "company_id",
        ],
        "sectors": [
            "id",
            "company_id",
        ],
        "stock_prices": [
            "id",
            "company_id",
            "date",
        ],
    }

    for name, columns in required_columns.items():
        df = data[name]

        missing = [column for column in columns if column not in df.columns]

        if missing:
            failures.append(
                {
                    "rule": "DQ-01",
                    "dataset": name,
                    "severity": "CRITICAL",
                    "message": f"Missing columns: {missing}",
                }
            )

    return failures


# ---------------------------------------------------------
# DQ-02: Duplicate business keys
# ---------------------------------------------------------


def validate_duplicates(data):
    failures = []

    for name in YEAR_KEY_DATASETS:
        df = data[name].copy()

        if "company_id" not in df.columns or "year" not in df.columns:
            continue

        temp = df.copy()

        temp["_company_key"] = temp["company_id"].apply(clean_company_id)

        temp["_year_key"] = temp["year"].apply(clean_year)

        duplicate_groups = (
            temp[
                temp.duplicated(
                    ["_company_key", "_year_key"],
                    keep=False,
                )
            ]
            .groupby(["_company_key", "_year_key"])
            .size()
            .reset_index(name="row_count")
        )

        for _, row in duplicate_groups.iterrows():
            failures.append(
                {
                    "rule": "DQ-02",
                    "dataset": name,
                    "severity": "CRITICAL",
                    "company_id": row["_company_key"],
                    "year": row["_year_key"],
                    "message": (
                        "Duplicate company/year business key "
                        f"found ({int(row['row_count'])} rows)"
                    ),
                }
            )

    return failures


# ---------------------------------------------------------
# DQ-03: Invalid company references
# ---------------------------------------------------------


def validate_company_references(data):
    failures = []

    companies = data["companies"].copy()

    valid_company_ids = set(companies["id"].apply(clean_company_id).dropna())

    for name in COMPANY_REFERENCE_DATASETS:

        if name not in data:
            continue

        df = data[name].copy()

        if "company_id" not in df.columns:
            continue

        referenced_ids = set(df["company_id"].apply(clean_company_id).dropna())

        invalid_ids = sorted(referenced_ids - valid_company_ids)

        for company_id in invalid_ids:
            failures.append(
                {
                    "rule": "DQ-03",
                    "dataset": name,
                    "severity": "CRITICAL",
                    "company_id": company_id,
                    "message": "Company ID not found in companies dataset",
                }
            )

    return failures


# ---------------------------------------------------------
# DQ-04: Null company IDs
# ---------------------------------------------------------


def validate_null_company_ids(data):
    failures = []

    for name in COMPANY_REFERENCE_DATASETS:

        df = data[name]

        if "company_id" not in df.columns:
            continue

        null_count = df["company_id"].isna().sum()

        if null_count > 0:
            failures.append(
                {
                    "rule": "DQ-04",
                    "dataset": name,
                    "severity": "CRITICAL",
                    "message": (f"{null_count} rows contain null company_id"),
                }
            )

    return failures


# ---------------------------------------------------------
# DQ-05: OPM consistency
# ---------------------------------------------------------


def validate_opm(data):
    failures = []

    df = data["profitandloss"].copy()

    required = [
        "company_id",
        "year",
        "sales",
        "operating_profit",
        "opm_percentage",
    ]

    if not all(column in df.columns for column in required):
        return failures

    sales = pd.to_numeric(
        df["sales"],
        errors="coerce",
    )

    operating_profit = pd.to_numeric(
        df["operating_profit"],
        errors="coerce",
    )

    reported_opm = pd.to_numeric(
        df["opm_percentage"],
        errors="coerce",
    )

    calculated_opm = (operating_profit / sales) * 100

    difference = (calculated_opm - reported_opm).abs()

    invalid = df[difference > 1].copy()

    for index in invalid.index:

        failures.append(
            {
                "rule": "DQ-05",
                "dataset": "profitandloss",
                "severity": "WARNING",
                "company_id": clean_company_id(df.loc[index, "company_id"]),
                "year": clean_year(df.loc[index, "year"]),
                "message": (
                    "Reported OPM differs from calculated OPM "
                    "by more than 1 percentage point"
                ),
            }
        )

    return failures


# ---------------------------------------------------------
# DQ-06: Non-positive sales
# ---------------------------------------------------------


def validate_sales(data):
    failures = []

    df = data["profitandloss"].copy()

    if "sales" not in df.columns:
        return failures

    sales = pd.to_numeric(
        df["sales"],
        errors="coerce",
    )

    invalid = df[sales <= 0]

    for index in invalid.index:

        failures.append(
            {
                "rule": "DQ-06",
                "dataset": "profitandloss",
                "severity": "WARNING",
                "company_id": clean_company_id(df.loc[index, "company_id"]),
                "year": clean_year(df.loc[index, "year"]),
                "message": "Sales is zero or negative",
            }
        )

    return failures


# ---------------------------------------------------------
# Main validation
# ---------------------------------------------------------


def validate_all_datasets(data):

    failures = []

    failures.extend(validate_required_columns(data))

    failures.extend(validate_duplicates(data))

    failures.extend(validate_company_references(data))

    failures.extend(validate_null_company_ids(data))

    failures.extend(validate_opm(data))

    failures.extend(validate_sales(data))

    return failures


# ---------------------------------------------------------
# Save report
# ---------------------------------------------------------


def save_report(failures):

    report_path = OUTPUT_DIR / "validation_failures.csv"

    if failures:
        df = pd.DataFrame(failures)
    else:
        df = pd.DataFrame(
            columns=[
                "rule",
                "dataset",
                "severity",
                "company_id",
                "year",
                "message",
            ]
        )

    df.to_csv(
        report_path,
        index=False,
    )

    return report_path


# ---------------------------------------------------------
# Report
# ---------------------------------------------------------


def print_report(failures):

    print()
    print("=" * 70)
    print("N100 FINANCIAL INTELLIGENCE - " "DATA QUALITY REPORT")
    print("=" * 70)

    rules = [
        "DQ-01",
        "DQ-02",
        "DQ-03",
        "DQ-04",
        "DQ-05",
        "DQ-06",
    ]

    for rule in rules:

        rule_failures = [x for x in failures if x["rule"] == rule]

        critical = sum(x["severity"] == "CRITICAL" for x in rule_failures)

        warning = sum(x["severity"] == "WARNING" for x in rule_failures)

        if critical or warning:
            print(f"{rule:<8} " f"CRITICAL={critical:<6} " f"WARNING={warning:<6}")

    total_critical = sum(x["severity"] == "CRITICAL" for x in failures)

    total_warning = sum(x["severity"] == "WARNING" for x in failures)

    print("-" * 70)
    print(f"Total CRITICAL : {total_critical}")
    print(f"Total WARNING  : {total_warning}")
    print(f"Total failures : {len(failures)}")

    report_path = save_report(failures)

    print(f"Report         : {report_path}")

    print("=" * 70)


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":

    data = load_all_datasets()

    failures = validate_all_datasets(data)

    print_report(failures)
