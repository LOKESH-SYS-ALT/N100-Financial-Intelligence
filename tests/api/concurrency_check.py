from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
from src.api.main import app
import time

ENDPOINTS = [
    "/api/v1/health",
    "/api/v1/companies",
    "/api/v1/companies/ABB",
    "/api/v1/screener",
    "/api/v1/sectors",
    "/api/v1/peers",
    "/api/v1/market/market-cap",
]

REQUESTS_PER_ENDPOINT = 5


def make_request(endpoint):
    client = TestClient(app)

    start = time.perf_counter()
    response = client.get(endpoint)
    elapsed = (time.perf_counter() - start) * 1000

    return endpoint, response.status_code, elapsed


print("DAY 43 - CONCURRENCY TEST")
print("=" * 90)

jobs = []

for endpoint in ENDPOINTS:
    for _ in range(REQUESTS_PER_ENDPOINT):
        jobs.append(endpoint)

start_all = time.perf_counter()

results = []

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(make_request, endpoint) for endpoint in jobs]

    for future in as_completed(futures):
        results.append(future.result())

total_elapsed = (time.perf_counter() - start_all) * 1000

failed = [result for result in results if result[1] != 200]

print(f"Total concurrent requests: {len(results)}")
print(f"Successful requests: {len(results) - len(failed)}")
print(f"Failed requests: {len(failed)}")
print(f"Total wall time: {total_elapsed:.2f} ms")

print("-" * 90)

for endpoint in ENDPOINTS:
    endpoint_times = [result[2] for result in results if result[0] == endpoint]

    print(
        f"{endpoint:<45}"
        f"avg={sum(endpoint_times) / len(endpoint_times):7.2f} ms  "
        f"max={max(endpoint_times):7.2f} ms"
    )

assert not failed
assert len(results) == 35

print("=" * 90)
print("CONCURRENCY TEST PASSED")
print("All concurrent requests returned HTTP 200")
