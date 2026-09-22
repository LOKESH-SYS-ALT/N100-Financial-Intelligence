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

 

