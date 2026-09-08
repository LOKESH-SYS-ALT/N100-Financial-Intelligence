from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_api_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "N100 Financial Intelligence API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"


def test_health():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["database"] == "ok"
    assert data["version"] == "1.0.0"
    assert data["db_row_counts"]["companies"] == 92


def test_list_companies():
    response = client.get("/api/v1/companies")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 92
    assert len(data["companies"]) == 92


def test_search_company():
    response = client.get("/api/v1/companies?search=ABB")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert data["companies"][0]["company_id"] == "ABB"


def test_get_company_profile():
    response = client.get("/api/v1/companies/ABB")

    assert response.status_code == 200

    data = response.json()

    assert data["company_id"] == "ABB"
    assert data["company_name"]
    assert data["sector"]


def test_invalid_company_profile():
    response = client.get("/api/v1/companies/XXXX")

    assert response.status_code == 404


def test_profit_and_loss():
    response = client.get("/api/v1/companies/ABB/financials/pl")

    assert response.status_code == 200

    data = response.json()

    assert data["company_id"] == "ABB"
    assert data["count"] > 0
    assert len(data["profit_and_loss"]) == data["count"]


def test_balance_sheet():
    response = client.get("/api/v1/companies/ABB/financials/bs")

    assert response.status_code == 200

    data = response.json()

    assert data["company_id"] == "ABB"
    assert data["count"] > 0


def test_cashflow():
    response = client.get("/api/v1/companies/ABB/financials/cashflow")

    assert response.status_code == 200

    data = response.json()

    assert data["company_id"] == "ABB"
    assert data["count"] > 0


def test_financial_ratios():
    response = client.get("/api/v1/companies/ABB/financials/ratios")

    assert response.status_code == 200

    data = response.json()

    assert data["company_id"] == "ABB"
    assert data["count"] > 0


def test_company_documents():
    response = client.get("/api/v1/companies/TCS/documents")

    assert response.status_code == 200

    data = response.json()

    assert data["company_id"] == "TCS"
    assert data["count"] == 16
    assert len(data["documents"]) == 16


def test_screener():
    response = client.get("/api/v1/screener")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 92
    assert len(data["results"]) == 92


def test_screener_with_roe_filter():
    response = client.get("/api/v1/screener?min_roe=20")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 34


def test_sectors():
    response = client.get("/api/v1/sectors")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 10
    assert len(data["sectors"]) == 10


def test_sector_companies():
    response = client.get("/api/v1/sectors/Financials/companies")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 23
    assert len(data["companies"]) == 23


def test_peers():
    response = client.get("/api/v1/peers")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 56


def test_company_peers():
    response = client.get("/api/v1/peers/TCS")

    assert response.status_code == 200

    data = response.json()

    assert data["company_id"] == "TCS"
    assert data["count"] > 0


def test_peer_compare():
    response = client.get("/api/v1/peers/compare?company_id=TCS")

    assert response.status_code == 200

    data = response.json()

    assert data["company_id"] == "TCS"
    assert data["peer_group_name"] == "IT Services"
    assert data["count"] == 5


def test_market_cap():
    response = client.get("/api/v1/market/market-cap")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 552


def test_portfolio_stats():
    response = client.get("/api/v1/market/portfolio-stats")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 5


def test_reports_status():
    response = client.get("/api/v1/reports/status")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_tearsheet_endpoint():
    response = client.get("/api/v1/reports/companies/ABB/tearsheet")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")


def test_invalid_tearsheet():
    response = client.get("/api/v1/reports/companies/XXXX/tearsheet")

    assert response.status_code == 404
