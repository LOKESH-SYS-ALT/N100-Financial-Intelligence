"""
N100 Financial Intelligence
Sprint 6 - Day 36
KMeans Financial Clustering
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"
CASHFLOW_PATH = PROJECT_ROOT / "output" / "cashflow_intelligence.xlsx"
ELBOW_PATH = PROJECT_ROOT / "reports" / "elbow_plot.png"
OUTPUT_PATH = PROJECT_ROOT / "output" / "cluster_labels.csv"


FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


def load_data():
    """Load latest annual KPI data and FCF CAGR data."""
    import sqlite3

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            return_on_equity_pct,
            debt_to_equity,
            revenue_cagr_5yr,
            operating_profit_margin_pct
        FROM financial_ratios
        """,
        conn,
    )

    sectors = pd.read_sql(
        """
        SELECT
            company_id,
            broad_sector
        FROM sectors
        """,
        conn,
    )

    conn.close()

    cashflow = pd.read_excel(CASHFLOW_PATH)

    return ratios, sectors, cashflow


def select_latest_annual(ratios):
    """Select the latest available annual row for each company.

    Prefer March annual data when available. For companies without
    a March annual row, use their latest available annual row.
    """
    df = ratios.copy()
    df["year_text"] = df["year"].astype(str).str.strip()
    df["year_num"] = pd.to_numeric(
        df["year_text"].str.extract(r"(20\d{2}|19\d{2})")[0],
        errors="coerce",
    )
    df = df.dropna(subset=["year_num"])

    df["is_march"] = df["year_text"].str.lower().str.startswith("mar")

    march = df[df["is_march"]].copy()
    non_march = df[~df["is_march"]].copy()

    latest_march = march.sort_values(["company_id", "year_num"]).drop_duplicates(
        subset=["company_id"], keep="last"
    )

    missing_march = set(df["company_id"]) - set(latest_march["company_id"])

    fallback = (
        non_march[non_march["company_id"].isin(missing_march)]
        .sort_values(["company_id", "year_num"])
        .drop_duplicates(subset=["company_id"], keep="last")
    )

    latest = pd.concat([latest_march, fallback], ignore_index=True)

    return latest


def add_fcf_cagr(df, cashflow):
    """Join five-year FCF CAGR to the clustering dataset."""
    fcf = cashflow[
        [
            "company_id",
            "fcf_cagr_5yr",
        ]
    ].copy()

    fcf = fcf.drop_duplicates(
        subset=["company_id"],
        keep="last",
    )

    df = df.merge(
        fcf,
        on="company_id",
        how="left",
    )

    return df


def impute_sector_median(df, sectors):
    """Impute missing feature values using broad-sector medians."""
    df = df.merge(
        sectors,
        on="company_id",
        how="left",
    )

    for feature in FEATURES:
        sector_medians = df.groupby("broad_sector")[feature].transform("median")

        df[feature] = df[feature].fillna(sector_medians)

        # Final fallback only if a whole sector has no value.
        df[feature] = df[feature].fillna(df[feature].median())

    return df


def generate_elbow_plot(X):
    """Generate elbow plot for k=2 through k=10."""
    inertias = []

    for k in range(2, 11):
        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10,
        )

        model.fit(X)

        inertias.append(model.inertia_)

    ELBOW_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(figsize=(8, 5))
    plt.plot(
        range(2, 11),
        inertias,
        marker="o",
    )
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Inertia")
    plt.title("KMeans Elbow Plot")
    plt.xticks(range(2, 11))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        ELBOW_PATH,
        dpi=150,
    )
    plt.close()


def run_clustering():
    """Run KMeans clustering and save cluster labels."""
    ratios, sectors, cashflow = load_data()

    latest = select_latest_annual(ratios)

    latest = add_fcf_cagr(
        latest,
        cashflow,
    )

    latest = impute_sector_median(
        latest,
        sectors,
    )

    missing = latest[FEATURES].isna().sum()

    if missing.any():
        raise ValueError(f"Missing feature values remain: {missing.to_dict()}")

    scaler = StandardScaler()

    X = scaler.fit_transform(latest[FEATURES])

    generate_elbow_plot(X)

    model = KMeans(
        n_clusters=5,
        random_state=42,
        n_init=10,
    )

    labels = model.fit_predict(X)

    distances = model.transform(X)

    assigned_distance = distances[
        range(len(labels)),
        labels,
    ]

    result = pd.DataFrame(
        {
            "company_id": latest["company_id"].values,
            "cluster_id": labels,
            "distance_from_centroid": assigned_distance,
        }
    )

    result["cluster_name"] = result["cluster_id"].map(
        {
            0: "Archetype 1",
            1: "Archetype 2",
            2: "Archetype 3",
            3: "Archetype 4",
            4: "Archetype 5",
        }
    )

    result = result[
        [
            "company_id",
            "cluster_id",
            "cluster_name",
            "distance_from_centroid",
        ]
    ]

    result = result.sort_values("company_id")

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("DAY 36 - KMEANS CLUSTERING")
    print(f"Companies clustered: {len(result)}")
    print(
        "Unique companies:",
        result["company_id"].nunique(),
    )
    print(
        "Clusters:",
        result["cluster_id"].nunique(),
    )
    print()
    print("Cluster distribution:")
    print(result["cluster_id"].value_counts().sort_index())
    print()
    print(f"Cluster labels: {OUTPUT_PATH}")
    print(f"Elbow plot: {ELBOW_PATH}")

    return result


if __name__ == "__main__":
    run_clustering()
