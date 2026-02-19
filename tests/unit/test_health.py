from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_metrics_endpoint():
    r = client.get("/metrics")
    # should return prometheus format and 200 even if empty
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")
    assert "app_requests_total" in r.text
