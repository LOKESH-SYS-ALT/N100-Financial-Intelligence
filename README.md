\# N100 Financial Intelligence Platform



A production-oriented financial analytics platform for the Nifty 100 companies. The project combines data engineering, financial KPI analysis, screening, peer intelligence, clustering, REST APIs, dashboards, NLP-based pros and cons, and automated PDF reporting.



\## Project Overview



N100 Financial Intelligence provides a unified analytics workflow for Nifty 100 companies.



\### Core capabilities



\* ETL pipeline for structured financial datasets

\* Financial KPI calculation and validation

\* Company screening and configurable presets

\* Peer-group analysis and comparison

\* Financial health scoring

\* Cash-flow intelligence and distress alerts

\* Capital allocation pattern analysis

\* NLP-based pros and cons generation

\* KMeans company clustering

\* Streamlit analytics dashboard

\* FastAPI REST API

\* Automated company and sector PDF reports

\* Portfolio-level analytics

\* Automated test suite and API integration tests



\## Technology Stack



\* Python

\* Pandas

\* NumPy

\* SQLite

\* Scikit-learn

\* FastAPI

\* Uvicorn

\* Streamlit

\* ReportLab

\* Matplotlib

\* Seaborn

\* Pytest

\* Black

\* Ruff



\## Project Structure



```text

N100-Financial-Intelligence/

│

├── data/

│   ├── raw/

│   └── nifty100.db

│

├── output/

│   ├── analysis\_parsed.csv

│   ├── cashflow\_intelligence.xlsx

│   ├── distress\_alerts.csv

│   ├── pattern\_changes.csv

│   ├── portfolio\_stats.csv

│   ├── pros\_cons\_generated.csv

│   └── valuation\_summary.xlsx

│

├── reports/

│   ├── tearsheets/

│   ├── sector\_reports/

│   ├── portfolio/

│   ├── analyst\_guide.pdf

│   ├── correlation\_heatmap.png

│   └── elbow\_plot.png

│

├── src/

│   ├── analytics/

│   ├── api/

│   │   └── routers/

│   ├── dashboard/

│   ├── etl/

│   ├── nlp/

│   └── reports/

│

├── tests/

│   ├── api/

│   ├── etl/

│   ├── kpi/

│   └── screener/

│

├── requirements.txt

├── README.md

└── .gitignore

```



\## Analytics Modules



\### Financial KPIs



The platform calculates and analyses financial indicators including:



\* ROE

\* ROCE

\* ROA

\* Operating Profit Margin

\* Debt-to-Equity

\* Interest Coverage

\* Asset Turnover

\* Revenue CAGR

\* PAT CAGR

\* EPS CAGR

\* Free Cash Flow metrics



\### Screener



Companies can be filtered using configurable financial criteria.



Example filters include:



\* Minimum ROE

\* Maximum Debt-to-Equity

\* Minimum Revenue CAGR

\* Financial quality characteristics

\* Growth characteristics

\* Dividend characteristics



\## Clustering



The platform uses KMeans clustering to group companies into five financial archetypes.



Clustering features include:



\* ROE

\* Debt-to-Equity

\* Revenue CAGR

\* Free Cash Flow CAGR

\* Operating Profit Margin



Missing clustering values are handled through sector-level median imputation before feature scaling.



\## NLP Intelligence



The NLP module processes company analysis information and generates structured:



\* Pros

\* Cons

\* Validation outputs

\* Parse failure reports



Fallback rules are used when source information is incomplete so that companies can still receive baseline analytical coverage.



\## Cash Flow Intelligence



Cash-flow analytics evaluate:



\* Operating cash flow

\* Investing cash flow

\* Financing cash flow

\* Free cash flow

\* Cash-flow quality

\* Free cash-flow conversion

\* Distress indicators



Companies without available raw cash-flow data are not assigned invented values.



\## Capital Allocation Intelligence



The platform identifies capital allocation patterns such as:



\* Shareholder Returns

\* Reinvestor

\* Growth Funded by Debt

\* Liquidating Assets

\* Cash Accumulator

\* Distress Signal

\* Mixed

\* Pre-Revenue



\## Dashboard



The Streamlit dashboard provides multiple analytical screens covering:



1\. Home

2\. Company Profile

3\. Screener

4\. Peer Intelligence

5\. Trends

6\. Sectors

7\. Capital Allocation

8\. Reports



Run the dashboard with:



```powershell

streamlit run src/dashboard/app.py

```



The dashboard is available locally through the Streamlit URL displayed in the terminal.



\## REST API



The project provides a FastAPI REST API under `/api/v1`.



The API includes endpoints for:



\* Health monitoring

\* Company listing and filtering

\* Company profiles

\* Profit and loss

\* Balance sheet

\* Cash flow

\* Financial ratios

\* Company documents

\* Screener

\* Sector analysis

\* Sector companies

\* Peer groups

\* Peer comparison

\* Market-cap data

\* Portfolio statistics

\* Company tearsheets



Run the API with:



```powershell

uvicorn src.api.main:app --reload

```



API documentation:



```text

/docs

```



\## Testing



The project uses Pytest for automated validation.



Run the complete test suite:



```powershell

pytest -q

```



The test suite covers:



\* Normalization

\* ETL loading

\* Data validation

\* Financial KPIs

\* Screener engine

\* API endpoints

\* Integration behaviour



\## Code Quality



Code formatting is maintained using Black.



```powershell

python -m black src tests

```



Ruff is used for linting when available.



```powershell

ruff check src tests

```



\## Reports



The reporting layer generates:



\* Individual company tearsheets

\* Sector reports

\* Portfolio summary report

\* Analyst guide

\* Supporting analytics charts



Reports are stored under the `reports/` directory.



\## Data Quality



The ETL validation layer checks data quality rules including:



\* Required columns

\* Duplicate company/year records

\* Company references

\* Missing company IDs

\* Operating margin consistency

\* Invalid sales values



The project preserves source data and does not fabricate missing financial values.



\## Development Environment



Recommended environment:



```powershell

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

```



Install dependencies:



```powershell

pip install -r requirements.txt

```



\## Important Notes



This project is intended for educational, analytical, and portfolio-research purposes.



Financial data and analytical outputs should not be interpreted as investment advice.



