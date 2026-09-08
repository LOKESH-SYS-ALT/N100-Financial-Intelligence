from pathlib import Path

import pandas as pd

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


# ============================================================
# DATASET CONFIGURATION
# ============================================================

DATASETS = {
    "companies": "companies.xlsx",
    "profitandloss": "profitandloss.xlsx",
    "balancesheet": "balancesheet.xlsx",
    "cashflow": "cashflow.xlsx",
    "analysis": "analysis.xlsx",
    "documents": "documents.xlsx",
    "prosandcons": "prosandcons.xlsx",
    "financial_ratios": "financial_ratios.xlsx",
    "market_cap": "market_cap.xlsx",
    "peer_groups": "peer_groups.xlsx",
    "sectors": "sectors.xlsx",
    "stock_prices": "stock_prices.xlsx",
}


# ============================================================
# HEADER CONFIGURATION
# ============================================================

HEADER_ROW_1_FILES = {
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
}


# ============================================================
# DATASETS WHERE COMPANY + YEAR MUST BE UNIQUE
# ============================================================

UNIQUE_COMPANY_YEAR_FILES = {
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "financial_ratios.xlsx",
}


# ============================================================
# LOAD SINGLE EXCEL FILE
# ============================================================


def load_excel(filename):
    """
    Load one Excel dataset from data/raw/.

    Parameters
    ----------
    filename : str
        Excel file name.

    Returns
    -------
    pandas.DataFrame
        Loaded and cleaned DataFrame.
    """

    file_path = RAW_DATA_DIR / filename

    # --------------------------------------------------------
    # Check whether file exists
    # --------------------------------------------------------

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    # --------------------------------------------------------
    # Select correct header row
    # --------------------------------------------------------

    if filename in HEADER_ROW_1_FILES:
        header_row = 1
    else:
        header_row = 0

    # --------------------------------------------------------
    # Read Excel file
    # --------------------------------------------------------

    df = pd.read_excel(file_path, header=header_row)

    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------

    df.columns = df.columns.astype(str).str.strip()

    # --------------------------------------------------------
    # Remove completely empty rows
    # --------------------------------------------------------

    df = df.dropna(how="all").reset_index(drop=True)

    # --------------------------------------------------------
    # Remove exact duplicate rows
    # --------------------------------------------------------

    df = df.drop_duplicates().reset_index(drop=True)

    # --------------------------------------------------------
    # Enforce unique company/year business key
    # --------------------------------------------------------

    if (
        "company_id" in df.columns
        and "year" in df.columns
        and filename in UNIQUE_COMPANY_YEAR_FILES
    ):

        df = df.drop_duplicates(
            subset=["company_id", "year"], keep="first"
        ).reset_index(drop=True)

    return df


# ============================================================
# LOAD ALL 12 DATASETS
# ============================================================


def load_all_datasets():
    """
    Load all 12 N100 datasets.

    Returns
    -------
    dict[str, pandas.DataFrame]
        Dictionary containing all loaded datasets.
    """

    loaded_data = {}

    for name, filename in DATASETS.items():
        loaded_data[name] = load_excel(filename)

    return loaded_data


# ============================================================
# DISPLAY DATASET SUMMARY
# ============================================================


def print_dataset_summary(data):
    """
    Print dataset names and row counts.
    """

    print("\n" + "=" * 60)
    print("N100 FINANCIAL INTELLIGENCE - DATASET SUMMARY")
    print("=" * 60)

    for name, df in data.items():
        print(f"{name:<20} : {len(df):>6} rows")

    print("=" * 60)
    print(f"Total datasets loaded : {len(data)}")
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    data = load_all_datasets()

    print_dataset_summary(data)
