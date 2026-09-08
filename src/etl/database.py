from pathlib import Path
import sqlite3

from src.etl.loader import load_all_datasets

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"


# ============================================================
# TABLE CONFIGURATION
# ============================================================

TABLES = {
    "companies": "companies",
    "profitandloss": "profitandloss",
    "balancesheet": "balancesheet",
    "cashflow": "cashflow",
    "analysis": "analysis",
    "documents": "documents",
    "prosandcons": "prosandcons",
    "financial_ratios": "financial_ratios",
    "market_cap": "market_cap",
    "peer_groups": "peer_groups",
    "sectors": "sectors",
    "stock_prices": "stock_prices",
}


# ============================================================
# NORMALIZE COMPANY IDs
# ============================================================


def normalize_company_ids(series):
    """
    Normalize company IDs for universe comparison.
    """

    return series.astype(str).str.strip().str.upper()


# ============================================================
# BUILD MASTER ANALYTICAL UNIVERSE
# ============================================================


def get_master_universe(data):
    """
    Build the official 92-company analytical universe.

    sectors.xlsx is treated as the master universe because
    it contains exactly 92 companies.
    """

    sectors = data["sectors"]

    universe = set(normalize_company_ids(sectors["company_id"]))

    print(f"Master analytical universe: {len(universe)} companies")

    if len(universe) != 92:
        raise ValueError(
            f"Expected 92 companies in analytical universe, " f"found {len(universe)}"
        )

    return universe


# ============================================================
# FILTER DATASETS TO MASTER UNIVERSE
# ============================================================


def filter_to_master_universe(data, universe):
    """
    Keep only companies belonging to the official
    92-company analytical universe.

    Raw Excel files are NOT modified.
    """

    filtered = {}

    for dataset_name, df in data.items():

        df = df.copy()

        # ----------------------------------------------------
        # Companies master table
        # ----------------------------------------------------

        if dataset_name == "companies":

            ids = normalize_company_ids(df["id"])

            df = df.loc[ids.isin(universe)].copy()

        # ----------------------------------------------------
        # All datasets containing company_id
        # ----------------------------------------------------

        elif "company_id" in df.columns:

            ids = normalize_company_ids(df["company_id"])

            df = df.loc[ids.isin(universe)].copy()

        # ----------------------------------------------------
        # Store filtered dataframe
        # ----------------------------------------------------

        filtered[dataset_name] = df.reset_index(drop=True)

    return filtered


# ============================================================
# CREATE DATABASE
# ============================================================


def create_database():

    print()
    print("=" * 70)
    print("BUILDING N100 FINANCIAL INTELLIGENCE DATABASE")
    print("=" * 70)

    # --------------------------------------------------------
    # Load raw datasets
    # --------------------------------------------------------

    data = load_all_datasets()

    print()
    print("Loaded datasets:", len(data))

    # --------------------------------------------------------
    # Establish master 92-company universe
    # --------------------------------------------------------

    universe = get_master_universe(data)

    # --------------------------------------------------------
    # Filter all datasets
    # --------------------------------------------------------

    data = filter_to_master_universe(data, universe)

    print()
    print("Filtered dataset sizes:")
    print("-" * 70)

    for dataset_name, df in data.items():

        print(f"{dataset_name:<20} : " f"{len(df):>6} rows")

    # --------------------------------------------------------
    # Create data directory
    # --------------------------------------------------------

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # Remove old database
    # --------------------------------------------------------

    if DB_PATH.exists():

        DB_PATH.unlink()

        print()
        print("Old database removed.")

    # --------------------------------------------------------
    # Create SQLite database
    # --------------------------------------------------------

    con = sqlite3.connect(DB_PATH)

    try:

        # Enable foreign keys
        con.execute("PRAGMA foreign_keys = ON")

        # ----------------------------------------------------
        # Write all tables
        # ----------------------------------------------------

        for dataset_name, table_name in TABLES.items():

            df = data[dataset_name].copy()

            df.to_sql(
                table_name,
                con,
                if_exists="replace",
                index=False,
            )

        con.commit()

    finally:

        con.close()

    print()
    print("Database created successfully.")
    print(f"Location: {DB_PATH}")


# ============================================================
# VERIFY DATABASE
# ============================================================


def verify_database():

    if not DB_PATH.exists():

        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    con = sqlite3.connect(DB_PATH)

    try:

        # ----------------------------------------------------
        # Get tables
        # ----------------------------------------------------

        query = """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """

        tables = [row[0] for row in con.execute(query).fetchall()]

        # ----------------------------------------------------
        # Print database report
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("N100 FINANCIAL INTELLIGENCE - DATABASE")
        print("=" * 70)

        print(f"Database : {DB_PATH}")

        print()
        print("Tables:")

        for table in tables:

            count = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]

            print(f"{table:<20} : " f"{count:>6} rows")

        print("-" * 70)
        print(f"Total tables : {len(tables)}")

        # ----------------------------------------------------
        # Verify company universe
        # ----------------------------------------------------

        company_count = con.execute("SELECT COUNT(*) FROM companies").fetchone()[0]

        sector_count = con.execute("SELECT COUNT(*) FROM sectors").fetchone()[0]

        print()
        print("UNIVERSE CHECK")
        print("-" * 70)
        print(f"Companies : {company_count}")
        print(f"Sectors   : {sector_count}")

        if company_count == 92 and sector_count == 92:

            print("92-company universe : PASS")

        else:

            print("92-company universe : FAIL")

        print("=" * 70)

    finally:

        con.close()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    create_database()

    verify_database()
