from pathlib import Path
import shutil
import pandas as pd

PROJECT_ROOT = Path.cwd()
COMPANIES_FILE = PROJECT_ROOT / "data" / "raw" / "companies.xlsx"

MISSING_COMPANIES = [
    "AGTL",
    "ULTRACEMCO",
    "UNIONBANK",
    "UNITDSPR",
    "VBL",
    "VEDL",
    "WIPRO",
    "ZOMATO",
    "ZYDUSLIFE",
]


def main():
    if not COMPANIES_FILE.exists():
        raise FileNotFoundError(
            f"companies.xlsx not found: {COMPANIES_FILE}"
        )

    backup_file = COMPANIES_FILE.with_name("companies_backup.xlsx")

    if not backup_file.exists():
        shutil.copy2(COMPANIES_FILE, backup_file)
        print("Backup created.")

    df = pd.read_excel(COMPANIES_FILE, header=1)

    df.columns = df.columns.astype(str).str.strip()

    if "id" not in df.columns:
        raise ValueError("Column 'id' not found in companies.xlsx")

    existing_ids = set(
        df["id"].astype(str).str.strip().str.upper()
    )

    rows_to_add = []

    for company_id in MISSING_COMPANIES:
        if company_id not in existing_ids:
            row = {column: None for column in df.columns}
            row["id"] = company_id

            if "company_name" in df.columns:
                row["company_name"] = company_id

            rows_to_add.append(row)

    if not rows_to_add:
        print("NO MISSING COMPANIES")
        return

    new_rows = pd.DataFrame(rows_to_add, columns=df.columns)

    df = pd.concat([df, new_rows], ignore_index=True)

    with pd.ExcelWriter(COMPANIES_FILE, engine="openpyxl") as writer:
        title_row = pd.DataFrame(
            [["N100 Companies"] + [None] * (len(df.columns) - 1)],
            columns=df.columns
        )

        title_row.to_excel(
            writer,
            index=False,
            header=False,
            startrow=0
        )

        df.to_excel(
            writer,
            index=False,
            startrow=1
        )

    verify_df = pd.read_excel(COMPANIES_FILE, header=1)

    verify_ids = set(
        verify_df["id"].astype(str).str.strip().str.upper()
    )

    still_missing = [
        company_id
        for company_id in MISSING_COMPANIES
        if company_id not in verify_ids
    ]

    print()
    print("=" * 60)
    print("MISSING COMPANIES ADDED")
    print("=" * 60)

    for row in rows_to_add:
        print(row["id"])

    print("-" * 60)
    print(f"Total added     : {len(rows_to_add)}")
    print(f"Total companies : {len(verify_df)}")

    if still_missing:
        print()
        print("STILL MISSING:")
        for company_id in still_missing:
            print(company_id)
    else:
        print()
        print("Verification: SUCCESS")
        print("All 9 required company IDs are present.")

    print("=" * 60)


if __name__ == "__main__":
    main()
