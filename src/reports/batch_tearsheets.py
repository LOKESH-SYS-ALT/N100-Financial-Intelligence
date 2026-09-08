from pathlib import Path
import sqlite3
import pandas as pd
from src.reports.tearsheet import build_tearsheet, PROJECT_ROOT

DB = PROJECT_ROOT / "data" / "nifty100.db"
OUT = PROJECT_ROOT / "reports" / "tearsheets"
SKIP = PROJECT_ROOT / "output" / "skipped_tearsheets.csv"

conn = sqlite3.connect(DB)
companies = pd.read_sql("SELECT id, company_name FROM companies ORDER BY id", conn)
pnl = pd.read_sql("SELECT company_id, year FROM profitandloss", conn)
conn.close()

OUT.mkdir(parents=True, exist_ok=True)
(PROJECT_ROOT / "output").mkdir(parents=True, exist_ok=True)

skipped = []
generated = 0
errors = []

for _, company in companies.iterrows():
    ticker = str(company["id"])
    name = str(company["company_name"])

    years = pnl[pnl["company_id"].astype(str) == ticker]["year"].astype(str)
    years = years[years.str.match(r"^(Mar|Sep|TTM)", case=False, na=False)].nunique()

    if years < 3:
        skipped.append(
            {
                "company_id": ticker,
                "company_name": name,
                "years_available": years,
                "reason": "Less than 3 years of data",
            }
        )
        continue

    try:
        pdf = build_tearsheet(ticker)
        generated += 1
        print(f"OK  {ticker}  {pdf.stat().st_size} bytes")
    except Exception as e:
        errors.append({"company_id": ticker, "company_name": name, "error": str(e)})
        print(f"ERROR  {ticker}: {e}")

pd.DataFrame(skipped).to_csv(SKIP, index=False)

print("=" * 60)
print("DAY 34 - BATCH TEARSHEETS")
print("=" * 60)
print(f"Companies in DB : {len(companies)}")
print(f"Generated PDFs  : {generated}")
print(f"Skipped         : {len(skipped)}")
print(f"Errors          : {len(errors)}")
print(f"Output          : {OUT}")

if errors:
    pd.DataFrame(errors).to_csv(
        PROJECT_ROOT / "output" / "tearsheet_generation_errors.csv", index=False
    )

print("=" * 60)
