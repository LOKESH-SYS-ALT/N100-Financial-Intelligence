# 📊 N100 Financial Intelligence Platform

> **Production-oriented financial analytics platform for Nifty 100 companies**

N100 Financial Intelligence is an end-to-end financial analytics platform that brings together **data engineering, financial KPI analysis, company screening, peer comparison, financial health analysis, clustering, REST APIs, dashboards, NLP intelligence, and automated reporting** into one workflow.

---

## 🚀 Project Overview

The platform analyzes financial information across **92 Nifty 100 companies** using multiple structured financial datasets.

### ✨ Core Capabilities

- 🔄 **ETL Pipeline** — Load, normalize, validate, and store financial datasets
- 📈 **Financial KPI Analysis** — ROE, ROCE, margins, growth, leverage, and more
- 🔎 **Company Screener** — Filter companies using configurable financial criteria
- 👥 **Peer Intelligence** — Compare companies with their peer groups
- ❤️ **Financial Health Score** — Evaluate company-level financial health
- 💰 **Cash Flow Intelligence** — Analyze cash generation and distress indicators
- 🏦 **Capital Allocation Intelligence** — Identify capital allocation patterns
- 🧠 **NLP Intelligence** — Generate structured pros and cons
- 🔬 **KMeans Clustering** — Group companies into financial archetypes
- 📊 **Streamlit Dashboard** — Interactive multi-screen analytics interface
- ⚡ **FastAPI REST API** — Programmatic access to analytics
- 📄 **Automated Reports** — Company tearsheets and sector reports
- 🧪 **Automated Testing** — ETL, KPI, screener, API, and integration tests

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| 🐍 Python | Core development |
| 🐼 Pandas | Data processing |
| 🔢 NumPy | Numerical computation |
| 🗄️ SQLite | Database |
| 🤖 Scikit-learn | Machine learning / clustering |
| ⚡ FastAPI | REST API |
| 🚀 Uvicorn | API server |
| 📊 Streamlit | Interactive dashboard |
| 📄 ReportLab | PDF report generation |
| 📈 Matplotlib | Visualization |
| 🎨 Seaborn | Statistical visualization |
| 🧪 Pytest | Automated testing |
| 🖤 Black | Code formatting |
| 🔍 Ruff | Linting |

---

# 📁 Project Structure

```text
N100-Financial-Intelligence/
│
├── 📂 data/
│   ├── 📂 raw/
│   └── 🗄️ nifty100.db
│
├── 📂 config/
│   └── screener_config.yaml
│
├── 📂 src/
│   ├── 📂 analytics/
│   ├── 📂 api/
│   │   └── 📂 routers/
│   ├── 📂 dashboard/
│   ├── 📂 etl/
│   ├── 📂 nlp/
│   ├── 📂 reports/
│   └── 📂 screener/
│
├── 📂 tests/
│   ├── 📂 api/
│   ├── 📂 etl/
│   ├── 📂 kpi/
│   └── 📂 screener/
│
├── 📂 scripts/
│
├── 📂 output/
│
├── 📂 reports/
│   ├── 📂 tearsheets/
│   ├── 📂 sector/
│   └── 📂 portfolio/
│
├── 📄 requirements.txt
├── 📄 pytest.ini
├── 📄 Makefile
├── 📄 README.md
└── 📄 .gitignore
⚙️ Installation & Setup
🏗️ System Architecture
                         ┌─────────────────────┐
                         │   Raw Excel Data    │
                         │    12 Datasets      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   ETL / Data Layer  │
                         │                     │
                         │ Loader              │
                         │ Normalizer          │
                         │ Validator           │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   SQLite Database   │
                         │    nifty100.db      │
                         └──────────┬──────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
          │  Analytics   │  │   Screener   │  │ Peer Engine  │
          │              │  │              │  │              │
          │ KPI / CAGR   │  │ Filters      │  │ Benchmarking │
          │ Ratios       │  │ Conditions   │  │ Comparisons  │
          │ Valuation    │  │              │  │              │
          └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
                 │                 │                 │
                 └─────────────────┼─────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
             ┌──────────────┐              ┌──────────────┐
             │  FastAPI     │              │  Streamlit   │
             │  REST API    │              │  Dashboard   │
             └──────┬───────┘              └──────┬───────┘
                    │                             │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │ Automated Reports   │
                         │ Tearsheets / Sector │
                         │ Portfolio Analysis  │
                         └─────────────────────┘
📌 Key Metrics
Metric	Project Value
🏢 Companies Analyzed	92
📂 Financial Datasets	12
📊 Dashboard Screens	8
🧠 ML Clusters	5
🧪 Automated Tests	154 passing
📄 Company Tearsheets	92
🏭 Sector Reports	10
⚡ API	FastAPI
🗄️ Database	SQLite
🚀 Release	v1.0
✨ Core Capabilities
🔄 Data Engineering
Multi-source Excel ingestion
Data normalization
Financial-year normalization
Stock ticker normalization
Schema validation
Data-quality rules
SQLite database loading
📈 Financial Analytics
Revenue growth
Profit growth
EPS
ROE
ROCE
Operating margins
Net margins
Debt-to-equity
Interest coverage
Free cash flow
Capital expenditure
Dividend payout
Valuation metrics
🔎 Company Screening

Configurable screening engine supporting financial criteria such as:

Profitability
Growth
Leverage
Valuation
Cash-flow characteristics
Return metrics
👥 Peer Intelligence
Peer-group comparison
Company benchmarking
Relative financial metrics
Sector-level comparison
❤️ Financial Health

Company-level financial health analysis combining multiple financial indicators into a structured health assessment.

💰 Cash Flow Intelligence
Operating cash flow analysis
Free cash flow analysis
Capital expenditure analysis
Cash conversion indicators
Financial distress indicators
🏦 Capital Allocation Intelligence

Analyzes how companies deploy capital across areas such as:

Capital expenditure
Dividends
Debt
Cash generation
Investment activity
🧠 NLP Intelligence

Processes company pros and cons information and generates structured analytical outputs for easier interpretation.

🔬 Machine Learning

Uses KMeans clustering to identify groups of companies with similar financial characteristics.

📊 Interactive Analytics

Streamlit-based dashboard with multiple analytical screens.

⚡ API Layer

FastAPI REST endpoints provide programmatic access to the underlying financial intelligence.

📄 Automated Reporting

Generates:

Company tearsheets
Sector reports
Portfolio summary
Analyst guide
Supporting analytical outputs
Data Engineering & ETL

The ETL layer is responsible for converting raw financial datasets into a validated analytical database.

ETL Pipeline
Excel Files
    ↓
Load
    ↓
Normalize
    ↓
Validate
    ↓
Transform
    ↓
SQLite
    ↓
Analytics Ready
Main ETL Components
Component	Responsibility
loader.py	Dataset ingestion and database loading
normalizer.py	Year and ticker normalization
validator.py	Data-quality and schema validation
database.py	SQLite database operations
Normalization

The pipeline handles:

Financial-year formats
Ticker formatting
Whitespace normalization
Consistent field representation

Example:

FY2024
2024
2024-25

are normalized into a consistent analytical representation.

📊 Financial Intelligence

The analytics layer calculates and organizes financial indicators across multiple dimensions.

Profitability

Examples:

ROE
ROCE
Operating Margin
Net Margin
Profit Growth
Growth

Examples:

Sales Growth
Profit Growth
Stock Price CAGR
EPS Growth
Leverage

Examples:

Debt-to-Equity
Interest Coverage
Total Debt
Borrowing trends
Cash Flow

Examples:

Operating Cash Flow
Free Cash Flow
Capital Expenditure
Cash conversion indicators
Valuation

Examples:

P/E
P/B
EV
EV/EBITDA
Dividend Yield
🔎 Company Screener

The screening engine allows companies to be filtered using configurable financial criteria.

Example screening workflow:

Financial Dataset
      ↓
Select Metrics
      ↓
Apply Conditions
      ↓
Filter Companies
      ↓
Rank / Compare Results

The screener can combine multiple financial dimensions such as:

Profitability
Growth
Leverage
Valuation
Returns
Cash flow

Configuration is maintained separately from core logic.

config/screener_config.yaml

This makes the screening framework easier to modify and extend.

👥 Peer Intelligence

Peer analysis compares companies against their relevant peer groups.

The workflow helps identify:

Relative profitability
Relative growth
Relative leverage
Valuation differences
Financial performance patterns
Company
   ↓
Peer Group
   ↓
Metric Comparison
   ↓
Relative Position
   ↓
Peer Intelligence
❤️ Financial Health Analysis

The platform evaluates company financial health using multiple financial indicators rather than relying on a single metric.

The analysis considers dimensions such as:

Profitability
Growth
Leverage
Cash generation
Returns
Financial stability

The result is a structured company-level financial health view that can be consumed through the dashboard, API, and reports.

💰 Cash Flow Intelligence

Cash flow analysis focuses on understanding the quality and sustainability of company cash generation.

Key areas include:

Operating cash flow
Investing cash flow
Financing cash flow
Free cash flow
Capital expenditure
Cash-flow trends
Distress indicators

This allows financial performance to be analyzed beyond accounting profit alone.

🏦 Capital Allocation Intelligence

Capital allocation analysis studies how companies deploy generated capital.

The platform evaluates patterns involving:

Cash Generation
      │
      ├── Capital Expenditure
      ├── Dividends
      ├── Debt
      └── Investments

This provides an additional layer of financial interpretation beyond traditional KPI analysis.

🔬 Machine Learning & Clustering

The platform uses KMeans clustering to identify groups of companies with similar financial characteristics.

Current Result
92 Companies
      ↓
Feature Preparation
      ↓
KMeans Clustering
      ↓
5 Financial Clusters
      ↓
Cluster Profiles

The clustering workflow helps identify financial archetypes based on selected company characteristics.

Supporting outputs include:

Cluster labels
Cluster profiles
Elbow analysis
Financial feature comparisons

The clustering results are used as an analytical segmentation layer rather than as a standalone prediction system.

🧠 NLP Intelligence

The NLP module processes qualitative company information such as:

Pros
Cons
Business observations

The platform converts these inputs into structured outputs that can be consumed alongside quantitative financial metrics.

This creates a combined analytical view:

Quantitative Financial Data
              +
Qualitative Company Information
              ↓
      Financial Intelligence
📊 Interactive Dashboard

The Streamlit dashboard provides an interactive interface for exploring the financial intelligence platform.

Dashboard Screens
1. 🏠 Home

High-level project and market overview.

2. 🏢 Company Profile

Company-level financial information and KPIs.

3. 🔎 Screener

Configurable financial screening.

4. 👥 Peers

Peer-group comparison and benchmarking.

5. 📈 Trends

Financial and market trend analysis.

6. 🏭 Sectors

Sector-level financial analysis.

7. 💰 Capital

Capital allocation intelligence.

8. 📄 Reports

Access to generated analytical reports.

⚡ REST API

The project exposes financial intelligence through a FastAPI REST API.

The API architecture is organized using modular routers.

src/api/
│
├── main.py
├── dependencies.py
│
└── routers/
    ├── companies.py
    ├── financials.py
    ├── health.py
    ├── market.py
    ├── peers.py
    ├── reports.py
    ├── screener.py
    └── sectors.py
API Categories
Health
Companies
Financials
Market
Peers
Reports
Screener
Sectors
Swagger Documentation

When the API is running:

http://127.0.0.1:8000/docs

FastAPI automatically provides interactive API documentation through Swagger UI.

📄 Automated Reporting

The reporting layer automates generation of financial intelligence outputs.

Company Tearsheets

Generated for:

92 Companies

Each tearsheet provides a structured company-level analytical view.

Sector Reports

Generated for:

10 Sectors

Sector reports provide aggregated and comparative sector-level intelligence.

Portfolio Summary

A portfolio-level analytical summary is also generated.

Supporting Reports

The project includes:

Analyst guide
Acceptance checklist
Portfolio summary
Sector reports
Company tearsheets
Analytical outputs
Validation outputs
🔍 Data Quality & Validation

Data quality is treated as a core part of the platform rather than an afterthought.

The validation workflow checks for issues such as:

Missing required fields
Schema mismatches
Invalid financial years
Invalid ticker values
Duplicate records
Data consistency problems
Critical data-quality failures
Raw Data
   ↓
Schema Validation
   ↓
Normalization
   ↓
Data Quality Rules
   ↓
Critical Failure Detection
   ↓
Validated Dataset

This ensures downstream analytics operate on structured and validated data.

🧪 Testing

The project uses Pytest for automated testing across multiple layers.

Test Areas
tests/
├── api/
├── etl/
├── kpi/
└── screener/

Testing includes:

ETL loading
Data normalization
Data validation
CAGR calculations
Cash-flow KPIs
Leverage analysis
Financial ratios
Screener engine
API endpoints
Integration behaviour
Latest Verification
154 passed
0 warnings

Additional verification:

python -m compileall -q src

completed successfully.
Follow these steps to run the project locally.

1️⃣ Clone the Repository
git clone https://github.com/LOKESH-SYS-ALT/N100-Financial-Intelligence.git
cd N100-Financial-Intelligence
2️⃣ Create Virtual Environment
python -m venv .venv
🪟 Windows PowerShell
.\.venv\Scripts\Activate.ps1

If PowerShell blocks script execution:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

Then activate again:

.\.venv\Scripts\Activate.ps1
3️⃣ Install Dependencies
pip install -r requirements.txt
🗄️ Database & ETL

The project uses SQLite to store the processed Nifty 100 financial data.

Database location:

data/nifty100.db
🔄 Run the ETL Pipeline

Load and process the raw datasets:

python -m src.etl.loader

The ETL workflow performs:

📥 Dataset loading
🧹 Data normalization
🔤 Ticker normalization
📅 Financial-year normalization
🔍 Data-quality validation
🗄️ SQLite database loading
📊 Run the Dashboard

Start the Streamlit dashboard:

streamlit run src/dashboard/app.py

After starting, Streamlit will display a local URL in the terminal.

Usually:

http://localhost:8501
🖥️ Dashboard Screens

The dashboard contains:

🏠 Home
🏢 Company Profile
🔎 Screener
👥 Peer Intelligence
📈 Trends
🏭 Sectors
💰 Capital Allocation
📄 Reports
⚡ Run the REST API

Start the FastAPI server:

uvicorn src.api.main:app --reload

API:

http://127.0.0.1:8000
📚 Swagger API Documentation

Open:

http://127.0.0.1:8000/docs

The API provides endpoints for:

❤️ Health monitoring
🏢 Company listing
🔎 Company filtering
📊 Company profiles
💹 Profit & Loss
🏦 Balance Sheet
💵 Cash Flow
📈 Financial Ratios
📄 Company Documents
🔎 Screener
🏭 Sector Analysis
👥 Peer Groups
🤝 Peer Comparison
💰 Market Capitalization
📊 Portfolio Statistics
📄 Company Tearsheets
🧪 Run Tests

The project includes automated tests covering the major components.

Run the complete test suite:

pytest -q
✅ Current Test Result
154 passed

Test coverage includes:

🔄 ETL loading
🔤 Data normalization
✅ Data validation
📈 CAGR calculations
💰 Cash-flow KPIs
🏦 Leverage analysis
📊 Financial ratios
🔎 Screener engine
⚡ API endpoints
🔗 Integration behaviour
📈 Financial KPI Analytics

The platform calculates and analyzes financial indicators including:

ROE
ROCE
ROA
Operating Profit Margin
Debt-to-Equity
Interest Coverage
Asset Turnover
Revenue CAGR
PAT CAGR
EPS CAGR
Free Cash Flow metrics
🔎 Company Screener

The screener supports configurable financial criteria.

Example filters include:

📈 Minimum ROE
🏦 Maximum Debt-to-Equity
📊 Minimum Revenue CAGR
💎 Financial quality
🚀 Growth characteristics
💰 Dividend characteristics

Screening rules can be configured through:

config/screener_config.yaml
🔬 Company Clustering

The platform uses KMeans clustering to group companies into five financial archetypes.

Clustering Features
ROE
Debt-to-Equity
Revenue CAGR
Free Cash Flow CAGR
Operating Profit Margin

Missing clustering values are handled using sector-level median imputation before feature scaling.

🧠 NLP Intelligence

The NLP module processes company analysis information and generates structured:

👍 Pros
👎 Cons
✅ Validation outputs
⚠️ Parse failure reports

Fallback rules are used when source information is incomplete so that companies can still receive baseline analytical coverage.

💰 Cash Flow Intelligence

Cash-flow analytics evaluate:

💵 Operating Cash Flow
🏗️ Investing Cash Flow
💳 Financing Cash Flow
💰 Free Cash Flow
📊 Cash-flow quality
🔄 Free Cash-flow conversion
🚨 Distress indicators

The platform does not fabricate missing financial values.

🏦 Capital Allocation Intelligence

The platform identifies capital allocation patterns such as:

👨‍💼 Shareholder Returns
🔄 Reinvestor
💳 Growth Funded by Debt
📉 Liquidating Assets
💰 Cash Accumulator
🚨 Distress Signal
🔀 Mixed
🌱 Pre-Revenue
📄 Automated Reporting

The reporting layer generates:

🏢 Company Reports

Individual company tearsheets containing financial and analytical information.

🏭 Sector Reports

Sector-level analysis for the available Nifty 100 sectors.

💼 Portfolio Summary

Portfolio-level analytics and summary information.

📚 Analyst Guide

Supporting documentation for interpreting the platform's outputs.

Reports are stored under:

reports/
✅ Data Quality

The ETL validation layer checks important data-quality rules including:

📋 Required columns
🔁 Duplicate company/year records
🔗 Company references
🆔 Missing company IDs
📊 Operating margin consistency
💵 Invalid sales values
🔍 Dataset consistency

The project preserves source data and does not fabricate missing financial values.

🖤 Code Quality
Black

Format source and test code:

python -m black src tests
Ruff

Run linting when Ruff is installed:

ruff check src tests

ℹ️ Ruff is optional for environments where it is not installed.

🧰 Development Environment

Recommended Python environment:

python -m venv .venv

Windows PowerShell:

.\.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt
🔄 Quick Start

If everything is already configured, the basic workflow is:

# 1. Clone
git clone https://github.com/LOKESH-SYS-ALT/N100-Financial-Intelligence.git

# 2. Enter project
cd N100-Financial-Intelligence

# 3. Create environment
python -m venv .venv

# 4. Activate - Windows PowerShell
.\.venv\Scripts\Activate.ps1

# 5. Install dependencies
pip install -r requirements.txt

# 6. Run ETL
python -m src.etl.loader

# 7. Run API
uvicorn src.api.main:app --reload

# 8. Run Dashboard
streamlit run src/dashboard/app.py

# 9. Run tests
pytest -q

💡 Tip: Run the API and Dashboard in separate terminals.

📌 Important Notes

This project is intended for:

🎓 Educational purposes
💼 Portfolio demonstration
📊 Financial analytics research
🧪 Technical experimentation

Financial data and analytical outputs should not be interpreted as investment advice.
📦 Project Status
Component	Status
🔄 ETL Pipeline	✅ Complete
🗄️ SQLite Database	✅ Complete
📊 Financial Analytics	✅ Complete
🔎 Screener	✅ Complete
👥 Peer Intelligence	✅ Complete
🔬 Clustering	✅ Complete
🧠 NLP Intelligence	✅ Complete
⚡ REST API	✅ Complete
📊 Streamlit Dashboard	✅ Complete
📄 PDF Reporting	✅ Complete
🧪 Automated Tests	✅ Complete
📚 Documentation	✅ Complete
🏁 Version

N100 Financial Intelligence — v1.0

Production-oriented financial analytics platform for Nifty 100 companies.


**“clone → setup → ETL → API → dashboard → tests” to one place**
🔄 Quick Start — final version
# 🔄 Quick Start

Follow these steps to run the N100 Financial Intelligence Platform locally.

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/LOKESH-SYS-ALT/N100-Financial-Intelligence.git
cd N100-Financial-Intelligence
2️⃣ Create & Activate Virtual Environment
python -m venv .venv

Windows PowerShell:

.\.venv\Scripts\Activate.ps1

If PowerShell blocks script execution:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

Then activate again:

.\.venv\Scripts\Activate.ps1
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Run ETL Pipeline

Load and validate the raw financial datasets into SQLite:

python -m src.etl.loader

Database:

data/nifty100.db
5️⃣ Run the API

Open a new terminal, activate the virtual environment, and run:

uvicorn src.api.main:app --reload

API:

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs
6️⃣ Run the Dashboard

Open another terminal, activate the virtual environment, and run:

streamlit run src/dashboard/app.py

Dashboard:

http://localhost:8501
7️⃣ Run Tests

Run the complete automated test suite:

pytest -q

Expected result:

154 passed
🏁 Complete Workflow
📥 Clone Repository
       ↓
🐍 Create Virtual Environment
       ↓
📦 Install Dependencies
       ↓
🔄 Run ETL Pipeline
       ↓
🗄️ SQLite Database
       ↓
⚡ Start FastAPI
       ↓
📊 Start Streamlit Dashboard
       ↓
🧪 Run Tests
       ↓
✅ N100 Financial Intelligence Platform

💡 Tip: Run the API and Streamlit Dashboard in separate terminals so both services can run simultaneously.


### One important correction ⚠️



```markdown
### ✅ Current Project Test Status

The latest project verification completed with:

```text
154 passed

Run the tests yourself with:

pytest -q

 

