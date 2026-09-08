from fastapi.testclient import TestClient
from src.api.main import app
import time
import statistics

client = TestClient(app)

endpoints = [
    "/api/v1/health",
    "/api/v1/companies",
    "/api/v1/companies/ABB",
    "/api/v1/screener",
    "/api/v1/sectors",
    "/api/v1/peers",
    "/api/v1/market/market-cap",
]

REQUESTS = 10

print("DAY 43 - REPEATED API PERFORMANCE")
print("=" * 90)

for endpoint in endpoints:
    times = []

    for _ in range(REQUESTS):
        start = time.perf_counter()
        response = client.get(endpoint)
        elapsed = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        times.append(elapsed)

    print(
        f"{endpoint:<45}"
        f"min={min(times):7.2f} ms  "
        f"avg={statistics.mean(times):7.2f} ms  "
        f"max={max(times):7.2f} ms"
    )

print("=" * 90)
print(f"Requests per endpoint: {REQUESTS}")
print("All requests returned HTTP 200")
