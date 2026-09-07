from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "output"
    / "capital_allocation.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "output"
    / "pattern_changes.csv"
)


def year_sort_key(value):
    """
    Convert financial year text into chronological
    sorting key.

    Supports formats such as:
    Mar 2024
    Mar-24
    Dec 2023
    TTM
    """

    import re

    value = str(value).strip()

    if value.upper() == "TTM":
        return (9999, 99)

    month_order = {
        "Mar": 3,
        "Jun": 6,
        "Sep": 9,
        "Dec": 12,
    }

    month = 0

    for name, number in month_order.items():
        if name.lower() in value.lower():
            month = number
            break

    # Four-digit year
    match = re.search(r"\b(20\d{2})\b", value)

    if match:
        year = int(match.group(1))
        return (year, month)

    # Two-digit year, e.g. Mar-13 -> 2013
    match = re.search(r"[- ](\d{2})$", value)

    if match:
        year = 2000 + int(match.group(1))
        return (year, month)

    return (9998, 99)

def build_pattern_changes():
    df = pd.read_csv(INPUT_FILE)

    df["year"] = df["year"].astype(str)

    # TTM is not an annual period.
    df = df[
        df["year"].str.upper() != "TTM"
    ].copy()

    # Chronological ordering.
    df["_sort_key"] = df["year"].apply(
        year_sort_key
    )

    df = df.sort_values(
        ["company_id", "_sort_key"]
    ).copy()

    df["previous_pattern"] = (
        df.groupby("company_id")["pattern_label"]
        .shift(1)
    )

    df["current_pattern"] = (
        df["pattern_label"]
    )

    df["pattern_changed"] = (
        df["previous_pattern"].notna()
        & (
            df["previous_pattern"]
            != df["current_pattern"]
        )
    )

    result = df[
        [
            "company_id",
            "year",
            "previous_pattern",
            "current_pattern",
            "pattern_changed",
        ]
    ].copy()

    result.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    return result


def validate_latest_year(df):
    annual_years = df["year"].unique()

    mar_years = [
        year for year in annual_years
        if str(year).strip().lower().startswith("mar")
    ]

    latest_year = max(mar_years, key=year_sort_key)

    latest = df[
        df["year"] == latest_year
    ].copy()

    print("=" * 60)
    print("DAY 32 - CAPITAL ALLOCATION")
    print("=" * 60)

    print(
        f"Latest annual year: {latest_year}"
    )

    print(
        f"Companies in latest year: "
        f"{latest['company_id'].nunique()}"
    )

    print("\nLatest-year pattern distribution:")

    print(
        latest["current_pattern"]
        .value_counts()
        .sort_index()
    )

    print(
        "\nTotal pattern changes:",
        int(
            df["pattern_changed"].sum()
        ),
    )

    print(
        "\nOutput:",
        OUTPUT_FILE,
    )

    print("=" * 60)


if __name__ == "__main__":

    result = build_pattern_changes()

    validate_latest_year(result)