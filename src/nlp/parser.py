import re
import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "analysis.xlsx"
PARSED_FILE = PROJECT_ROOT / "output" / "analysis_parsed.csv"
FAILURE_FILE = PROJECT_ROOT / "output" / "parse_failures.csv"
VALIDATION_FILE = PROJECT_ROOT / "output" / "cagr_validation.csv"


TARGET_FIELDS = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe",
]


PATTERN = re.compile(
    r"(\d+)\s*Years?:?\s*([-+]?\d+(?:\.\d+)?)%"
)


def parse_metric(text):
    """Parse values such as '10 Years: 21%'."""

    if pd.isna(text):
        return None

    text = str(text).strip()

    match = PATTERN.search(text)

    if not match:
        return None

    period_years = int(match.group(1))
    value_pct = float(match.group(2))

    return period_years, value_pct


def parse_analysis():
    """Parse analysis.xlsx into structured metric rows."""

    df = pd.read_excel(INPUT_FILE, header=1)

    parsed_rows = []
    failure_rows = []

    for _, row in df.iterrows():

        company_id = row.get("company_id")

        for metric_type in TARGET_FIELDS:

            raw_text = row.get(metric_type)

            parsed = parse_metric(raw_text)

            if parsed is None:

                failure_rows.append(
                    {
                        "company_id": company_id,
                        "metric_type": metric_type,
                        "raw_text": raw_text,
                    }
                )

                continue

            period_years, value_pct = parsed

            parsed_rows.append(
                {
                    "company_id": company_id,
                    "metric_type": metric_type,
                    "period_years": period_years,
                    "value_pct": value_pct,
                }
            )

    parsed_df = pd.DataFrame(
        parsed_rows,
        columns=[
            "company_id",
            "metric_type",
            "period_years",
            "value_pct",
        ],
    )

    failures_df = pd.DataFrame(
        failure_rows,
        columns=[
            "company_id",
            "metric_type",
            "raw_text",
        ],
    )

    PARSED_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    parsed_df.to_csv(
        PARSED_FILE,
        index=False,
    )

    failures_df.to_csv(
        FAILURE_FILE,
        index=False,
    )

    return parsed_df, failures_df


def cross_validate(parsed_df):
    """
    Compare parsed 5-year analysis metrics against
    the latest non-null Ratio Engine metrics.

    Divergence > 5% is flagged.
    """

    conn = sqlite3.connect(
        PROJECT_ROOT / "data" / "nifty100.db"
    )

    query = """
        SELECT
            company_id,
            year,
            revenue_cagr_5yr,
            pat_cagr_5yr,
            return_on_equity_pct
        FROM financial_ratios
    """

    ratio_df = pd.read_sql_query(
        query,
        conn,
    )

    conn.close()

    ratio_df["year_number"] = pd.to_numeric(
        ratio_df["year"]
        .astype(str)
        .str.extract(r"(\d{4})")[0],
        errors="coerce",
    )

    ratio_df = ratio_df.sort_values(
        ["company_id", "year_number"]
    )

    metric_map = {
        "compounded_sales_growth": "revenue_cagr_5yr",
        "compounded_profit_growth": "pat_cagr_5yr",
        "roe": "return_on_equity_pct",
    }

    parsed_5yr = parsed_df[
        parsed_df["period_years"] == 5
    ].copy()

    validation_rows = []

    for _, row in parsed_5yr.iterrows():

        company_id = row["company_id"]
        metric_type = row["metric_type"]
        analysis_value = row["value_pct"]

        ratio_column = metric_map.get(metric_type)

        if ratio_column is None:

            validation_rows.append(
                {
                    "company_id": company_id,
                    "metric_type": metric_type,
                    "analysis_value_pct": analysis_value,
                    "ratio_engine_value_pct": None,
                    "divergence_pct": None,
                    "divergence_flag": "NOT_COMPARABLE",
                }
            )

            continue

        company_rows = ratio_df[
            ratio_df["company_id"].astype(str)
            == str(company_id)
        ].copy()

        if company_rows.empty:

            validation_rows.append(
                {
                    "company_id": company_id,
                    "metric_type": metric_type,
                    "analysis_value_pct": analysis_value,
                    "ratio_engine_value_pct": None,
                    "divergence_pct": None,
                    "divergence_flag": "NO_RATIO_DATA",
                }
            )

            continue

        available = company_rows[
            company_rows[ratio_column].notna()
        ].copy()

        if available.empty:

            validation_rows.append(
                {
                    "company_id": company_id,
                    "metric_type": metric_type,
                    "analysis_value_pct": analysis_value,
                    "ratio_engine_value_pct": None,
                    "divergence_pct": None,
                    "divergence_flag": "NO_RATIO_DATA",
                }
            )

            continue

        ratio_value = float(
            available.iloc[-1][ratio_column]
        )

        if ratio_value == 0:

            divergence = None
            flag = "NO_RATIO_BASE"

        else:

            divergence = (
                abs(analysis_value - ratio_value)
                / abs(ratio_value)
                * 100
            )

            flag = (
                "DIVERGENCE"
                if divergence > 5
                else "MATCH"
            )

        validation_rows.append(
            {
                "company_id": company_id,
                "metric_type": metric_type,
                "analysis_value_pct": analysis_value,
                "ratio_engine_value_pct": ratio_value,
                "divergence_pct": divergence,
                "divergence_flag": flag,
            }
        )

    validation_df = pd.DataFrame(
        validation_rows,
        columns=[
            "company_id",
            "metric_type",
            "analysis_value_pct",
            "ratio_engine_value_pct",
            "divergence_pct",
            "divergence_flag",
        ],
    )

    validation_df.to_csv(
        VALIDATION_FILE,
        index=False,
    )

    return validation_df
if __name__ == "__main__":

    parsed_df, failures_df = parse_analysis()

    validation_df = cross_validate(
        parsed_df
    )

    print(f"Parsed rows: {len(parsed_df)}")
    print(f"Parse failures: {len(failures_df)}")

    print(
        f"Validation rows: {len(validation_df)}"
    )

    print(
        "Divergences >5%:",
        (
            validation_df["divergence_flag"]
            == "DIVERGENCE"
        ).sum(),
    )

    print(
        "Matches:",
        (
            validation_df["divergence_flag"]
            == "MATCH"
        ).sum(),
    )

    print(
        "Not comparable:",
        (
            validation_df["divergence_flag"]
            == "NOT_COMPARABLE"
        ).sum(),
    )

    print(
        f"\nParsed file: {PARSED_FILE}"
    )

    print(
        f"Failure file: {FAILURE_FILE}"
    )

    print(
        f"Validation file: {VALIDATION_FILE}"
    )

    print("\nValidation results:")

    if not validation_df.empty:
        print(
            validation_df.to_string(
                index=False
            )
        )