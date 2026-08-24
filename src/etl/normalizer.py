import re

import pandas as pd


# ============================================================
# NORMALIZE YEAR
# ============================================================

def normalize_year(value):
    """
    Convert different year formats into a standard integer year.

    Examples:
        2024      -> 2024
        2024.0    -> 2024
        "2024"    -> 2024
        "FY2024"  -> 2024
        "2024-25" -> 2024
    """

    if pd.isna(value):
        return None

    # Numeric values
    if isinstance(value, (int, float)):
        return int(value)

    # String values
    value = str(value).strip().upper()

    # Extract first 4-digit year
    match = re.search(r"(19|20)\d{2}", value)

    if match:
        return int(match.group())

    return None


# ============================================================
# NORMALIZE TICKER
# ============================================================

def normalize_ticker(value):
    """
    Normalize a company ticker/symbol.

    Examples:
        "TCS"      -> "TCS"
        " tcs "    -> "TCS"
        "TCS.NS"   -> "TCS"
        "TCS.BO"   -> "TCS"
    """

    if pd.isna(value):
        return None

    value = str(value).strip().upper()

    # Remove NSE/BSE suffixes
    value = re.sub(r"\.(NS|BO)$", "", value)

    return value


# ============================================================
# NORMALIZE COLUMN NAMES
# ============================================================

def normalize_columns(df):
    """
    Normalize DataFrame column names.

    Examples:
        " Company Name " -> "company_name"
        "Book Value"     -> "book_value"
    """

    df = df.copy()

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )

    return df


# ============================================================
# NORMALIZE NUMERIC COLUMNS
# ============================================================

def normalize_numeric(df, columns):
    """
    Convert selected columns to numeric values.

    Invalid values are converted to NaN.
    """

    df = df.copy()

    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


# ============================================================
# NORMALIZE DATE
# ============================================================

def normalize_date(df, column="date"):
    """
    Convert a date column into pandas datetime format.
    """

    df = df.copy()

    if column in df.columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    return df