from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"
REPORTS_DIR = PROJECT_ROOT / "reports"

CLUSTER_LABELS_PATH = OUTPUT_DIR / "cluster_labels.csv"
CASHFLOW_PATH = OUTPUT_DIR / "cashflow_intelligence.xlsx"

CLUSTER_PROFILES_PATH = OUTPUT_DIR / "cluster_profiles.csv"
CORRELATION_PATH = REPORTS_DIR / "correlation_heatmap.png"
SECTOR_OUTLIERS_PATH = OUTPUT_DIR / "sector_outliers.csv"
PORTFOLIO_STATS_PATH = OUTPUT_DIR / "portfolio_stats.csv"


# ============================================================
# FEATURES
# ============================================================

CLUSTER_FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]

CORRELATION_FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "return_on_capital_employed_pct",
    "return_on_assets_pct",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "operating_profit_margin_pct",
]


# ============================================================
# DATABASE
# ============================================================


def get_connection():
    """Create SQLite database connection."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    return sqlite3.connect(DB_PATH)


# ============================================================
# LATEST ANNUAL DATA
# ============================================================


def select_latest_annual(df):
    """
    Select latest annual row for every company.

    March annual rows are preferred.
    If March is unavailable, latest available annual
    row is selected.
    """

    df = df.copy()

    df["year"] = df["year"].astype(str)

    annual = df[
        ~df["year"]
        .str.upper()
        .str.contains(
            "TTM",
            na=False,
        )
    ].copy()

    if annual.empty:
        return annual

    annual["year_num"] = pd.to_numeric(
        annual["year"].str.extract(r"(\d{4})")[0],
        errors="coerce",
    )

    annual["is_march"] = annual["year"].str.contains(
        r"(?i)^Mar\s",
        regex=True,
        na=False,
    )

    annual = annual.sort_values(
        [
            "company_id",
            "is_march",
            "year_num",
        ],
        ascending=[
            True,
            False,
            False,
        ],
    )

    latest = annual.drop_duplicates(
        subset=["company_id"],
        keep="first",
    )

    return latest.drop(
        columns=[
            "year_num",
            "is_march",
        ],
        errors="ignore",
    )


# ============================================================
# LOAD DATA
# ============================================================


def load_cluster_data():
    """Load ratios, sectors, cashflow and cluster labels."""

    if not CLUSTER_LABELS_PATH.exists():
        raise FileNotFoundError(f"Missing: {CLUSTER_LABELS_PATH}")

    clusters = pd.read_csv(CLUSTER_LABELS_PATH)

    conn = get_connection()

    ratios = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            net_profit_margin_pct,
            operating_profit_margin_pct,
            return_on_equity_pct,
            debt_to_equity,
            interest_coverage,
            asset_turnover,
            free_cash_flow_cr,
            capex_cr,
            earnings_per_share,
            book_value_per_share,
            dividend_payout_ratio_pct,
            total_debt_cr,
            cash_from_operations_cr,
            return_on_capital_employed_pct,
            return_on_assets_pct,
            revenue_cagr_5yr,
            pat_cagr_5yr,
            eps_cagr_5yr,
            composite_quality_score
        FROM financial_ratios
        """,
        conn,
    )

    sectors = pd.read_sql(
        """
        SELECT
            company_id,
            broad_sector AS sector
        FROM sectors
        """,
        conn,
    )

    conn.close()

    latest_ratios = select_latest_annual(ratios)

    # --------------------------------------------------------
    # Cashflow intelligence
    # --------------------------------------------------------

    if CASHFLOW_PATH.exists():

        cashflow = pd.read_excel(CASHFLOW_PATH)

        cashflow.columns = [str(c).strip() for c in cashflow.columns]

        company_column = None

        for col in cashflow.columns:

            normalized = str(col).lower().replace(" ", "_").replace("-", "_")

            if normalized in [
                "company_id",
                "company",
                "ticker",
            ]:
                company_column = col
                break

        if company_column:

            cashflow = cashflow.rename(columns={company_column: "company_id"})

        fcf_column = None

        for col in cashflow.columns:

            normalized = str(col).lower().replace(" ", "_").replace("-", "_")

            if "fcf_cagr" in normalized or "free_cash_flow_cagr" in normalized:
                fcf_column = col
                break

        if fcf_column:

            cashflow = cashflow[
                [
                    "company_id",
                    fcf_column,
                ]
            ].copy()

            cashflow = cashflow.rename(columns={fcf_column: "fcf_cagr_5yr"})

            cashflow = cashflow.drop_duplicates(subset=["company_id"])

        else:

            cashflow = pd.DataFrame(
                columns=[
                    "company_id",
                    "fcf_cagr_5yr",
                ]
            )

    else:

        cashflow = pd.DataFrame(
            columns=[
                "company_id",
                "fcf_cagr_5yr",
            ]
        )

    # --------------------------------------------------------
    # Merge
    # --------------------------------------------------------

    df = latest_ratios.merge(
        sectors,
        on="company_id",
        how="left",
    )

    df = df.merge(
        cashflow,
        on="company_id",
        how="left",
    )

    df = df.merge(
        clusters[
            [
                "company_id",
                "cluster_id",
                "cluster_name",
                "distance_from_centroid",
            ]
        ],
        on="company_id",
        how="inner",
    )

    return df


# ============================================================
# IMPUTATION
# ============================================================


def impute_missing_features(df):
    """
    Fill missing clustering features using sector median.
    Overall median is used as final fallback.
    """

    df = df.copy()

    for feature in CLUSTER_FEATURES:

        df[feature] = pd.to_numeric(
            df[feature],
            errors="coerce",
        )

        sector_median = df.groupby("sector")[feature].transform("median")

        df[feature] = df[feature].fillna(sector_median)

        overall_median = df[feature].median()

        df[feature] = df[feature].fillna(overall_median)

    return df


# ============================================================
# UNIQUE DESCRIPTIVE CLUSTER NAMES
# ============================================================


def generate_cluster_names(profile):
    """
    Generate descriptive names for the five clusters.

    Names are assigned based on relative characteristics
    of growth, profitability and leverage.
    """

    p = profile.copy()

    # Rank-based scores
    p["growth_score"] = (
        p["revenue_cagr_5yr"].rank(pct=True) + p["fcf_cagr_5yr"].rank(pct=True)
    ) / 2

    p["quality_score"] = (
        p["return_on_equity_pct"].rank(pct=True)
        + p["operating_profit_margin_pct"].rank(pct=True)
    ) / 2

    p["leverage_score"] = 1 - p["debt_to_equity"].rank(pct=True)

    p["overall_score"] = p["growth_score"] + p["quality_score"] + p["leverage_score"]

    # Highest overall quality
    best_cluster = p["overall_score"].idxmax()

    # Highest growth
    growth_cluster = p["growth_score"].idxmax()

    # Lowest leverage
    low_de_cluster = p["debt_to_equity"].idxmin()

    # Highest leverage
    high_de_cluster = p["debt_to_equity"].idxmax()

    # Remaining cluster
    remaining = [
        idx
        for idx in p.index
        if idx
        not in [
            best_cluster,
            growth_cluster,
            low_de_cluster,
            high_de_cluster,
        ]
    ]

    names = {}

    names[best_cluster] = "Quality Leaders"

    if growth_cluster not in names:
        names[growth_cluster] = "Growth Compounders"

    if low_de_cluster not in names:
        names[low_de_cluster] = "Low-Leverage Compounders"

    if high_de_cluster not in names:
        names[high_de_cluster] = "High-Leverage Challengers"

    for cluster_id in remaining:

        if cluster_id not in names:

            names[cluster_id] = "Balanced Performers"

    # Final uniqueness safeguard
    used = set()

    for cluster_id in sorted(names.keys()):

        original = names[cluster_id]
        name = original

        if name in used:
            name = f"{original} " f"(Cluster {cluster_id})"

        names[cluster_id] = name
        used.add(name)

    return names


# ============================================================
# CLUSTER PROFILES
# ============================================================


def create_cluster_profiles(df):
    """Create cluster-level statistics."""

    profile = df.groupby("cluster_id")[CLUSTER_FEATURES].mean()

    profile["company_count"] = df.groupby("cluster_id")["company_id"].nunique()

    names = generate_cluster_names(profile)

    profile["cluster_name"] = profile.index.map(names)

    # Median values
    medians = df.groupby("cluster_id")[CLUSTER_FEATURES].median()

    for feature in CLUSTER_FEATURES:

        profile[f"{feature}_median"] = medians[feature]

    profile = profile.reset_index()

    # Reorder columns
    first_columns = [
        "cluster_id",
        "cluster_name",
        "company_count",
    ]

    other_columns = [c for c in profile.columns if c not in first_columns]

    profile = profile[first_columns + other_columns]

    CLUSTER_PROFILES_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    profile.to_csv(
        CLUSTER_PROFILES_PATH,
        index=False,
    )

    print(f"Cluster profiles saved: " f"{CLUSTER_PROFILES_PATH}")

    print(f"Cluster profile rows: " f"{len(profile)}")

    print("\nCluster names:")

    for _, row in profile.iterrows():

        print(
            f"  {row['cluster_id']}: "
            f"{row['cluster_name']} "
            f"({row['company_count']} companies)"
        )

    return profile


# ============================================================
# CORRELATION HEATMAP
# ============================================================


def create_correlation_heatmap(df):
    """
    Create correlation heatmap using the latest
    available annual observation for each company.

    This avoids TTM rows where several KPI fields
    may be unavailable.
    """

    conn = get_connection()

    ratios = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            return_on_equity_pct,
            debt_to_equity,
            interest_coverage,
            asset_turnover,
            return_on_capital_employed_pct,
            return_on_assets_pct,
            revenue_cagr_5yr,
            pat_cagr_5yr,
            eps_cagr_5yr,
            operating_profit_margin_pct
        FROM financial_ratios
        """,
        conn,
    )

    conn.close()

    ratios = select_latest_annual(ratios)

    ratios = ratios[
        [
            "company_id",
            *CORRELATION_FEATURES,
        ]
    ].copy()

    for feature in CORRELATION_FEATURES:

        ratios[feature] = pd.to_numeric(
            ratios[feature],
            errors="coerce",
        )

    # Keep all requested KPI columns.
    # Columns with some missing values remain present.
    available = [
        feature for feature in CORRELATION_FEATURES if feature in ratios.columns
    ]

    corr = ratios[available].corr()

    # Fill missing correlation values only
    # for visualization, without changing source data.
    heatmap_corr = corr.fillna(0)

    CORRELATION_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(figsize=(12, 10))

    sns.heatmap(
        heatmap_corr,
        annot=True,
        fmt=".2f",
        square=True,
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        linewidths=0.5,
    )

    plt.title("N100 Financial KPI Correlation Heatmap")

    plt.tight_layout()

    plt.savefig(
        CORRELATION_PATH,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()

    print(f"\nCorrelation KPIs: " f"{len(available)}")

    print(f"Correlation heatmap saved: " f"{CORRELATION_PATH}")

    return corr


# ============================================================
# SECTOR OUTLIERS
# ============================================================


def create_sector_outliers(df):
    """
    Detect sector-level outliers.

    Absolute z-score >= 2 on any clustering KPI
    marks the company as an outlier.
    """

    result = df.copy()

    z_columns = []

    for feature in CLUSTER_FEATURES:

        result[feature] = pd.to_numeric(
            result[feature],
            errors="coerce",
        )

        sector_mean = result.groupby("sector")[feature].transform("mean")

        sector_std = result.groupby("sector")[feature].transform("std")

        sector_std = sector_std.replace(
            0,
            pd.NA,
        )

        z_col = f"{feature}_zscore"

        result[z_col] = (result[feature] - sector_mean) / sector_std

        z_columns.append(z_col)

    result["max_abs_zscore"] = result[z_columns].abs().max(axis=1)

    result["is_outlier"] = result["max_abs_zscore"] >= 2

    output_columns = [
        "company_id",
        "sector",
        "cluster_id",
        "cluster_name",
        "max_abs_zscore",
        "is_outlier",
    ]

    result = result[output_columns + z_columns]

    result = result.sort_values(
        [
            "is_outlier",
            "max_abs_zscore",
        ],
        ascending=[
            False,
            False,
        ],
    )

    SECTOR_OUTLIERS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        SECTOR_OUTLIERS_PATH,
        index=False,
    )

    print(f"\nSector outliers saved: " f"{SECTOR_OUTLIERS_PATH}")

    print(f"Outlier rows: " f"{len(result)}")

    print(f"Outlier companies: " f"{result['is_outlier'].sum()}")

    return result


# ============================================================
# PORTFOLIO STATISTICS
# ============================================================


def create_portfolio_stats(df):
    """
    Calculate P10/P25/P50/P75/P90/Mean/Std
    for clustering features.
    """

    rows = []

    for feature in CLUSTER_FEATURES:

        series = pd.to_numeric(
            df[feature],
            errors="coerce",
        ).dropna()

        if series.empty:
            continue

        rows.append(
            {
                "kpi": feature,
                "p10": series.quantile(0.10),
                "p25": series.quantile(0.25),
                "p50": series.quantile(0.50),
                "p75": series.quantile(0.75),
                "p90": series.quantile(0.90),
                "mean": series.mean(),
                "std": series.std(),
            }
        )

    stats = pd.DataFrame(rows)

    PORTFOLIO_STATS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    stats.to_csv(
        PORTFOLIO_STATS_PATH,
        index=False,
    )

    print(f"\nPortfolio stats saved: " f"{PORTFOLIO_STATS_PATH}")

    print(f"Portfolio KPI rows: " f"{len(stats)}")

    return stats


# ============================================================
# MAIN
# ============================================================


def main():

    print("=" * 60)
    print("DAY 37 - CLUSTER PROFILES " "& PORTFOLIO INTELLIGENCE")
    print("=" * 60)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    df = load_cluster_data()

    print(f"\nCompanies loaded: " f"{df['company_id'].nunique()}")

    # --------------------------------------------------------
    # Imputation
    # --------------------------------------------------------

    df = impute_missing_features(df)

    print("Missing clustering features imputed.")

    # --------------------------------------------------------
    # Cluster profiles
    # --------------------------------------------------------

    profiles = create_cluster_profiles(df)

    # --------------------------------------------------------
    # Correlation
    # --------------------------------------------------------

    correlation = create_correlation_heatmap(df)

    # --------------------------------------------------------
    # Sector outliers
    # --------------------------------------------------------

    outliers = create_sector_outliers(df)

    # --------------------------------------------------------
    # Portfolio stats
    # --------------------------------------------------------

    stats = create_portfolio_stats(df)

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    print("\n" + "=" * 60)

    print("DAY 37 VALIDATION")

    print("=" * 60)

    print(f"Companies: " f"{df['company_id'].nunique()}")

    print(f"Clusters: " f"{df['cluster_id'].nunique()}")

    print(f"Profile rows: " f"{len(profiles)}")

    print(f"Correlation KPIs: " f"{len(correlation.columns)}")

    print(f"Outlier rows: " f"{len(outliers)}")

    print(f"Portfolio KPI rows: " f"{len(stats)}")

    print("\nOutput files:")

    print(f"  {CLUSTER_PROFILES_PATH}")

    print(f"  {CORRELATION_PATH}")

    print(f"  {SECTOR_OUTLIERS_PATH}")

    print(f"  {PORTFOLIO_STATS_PATH}")

    print("\nDAY 37 COMPLETE")


if __name__ == "__main__":
    main()
