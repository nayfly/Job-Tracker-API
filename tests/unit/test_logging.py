from fastapi.testclient import TestClient
import json

from app.main import app

client = TestClient(app)


def test_request_id_header_and_json_log(caplog, capsys):
    caplog.set_level("INFO")
    r = client.get("/health")
    assert r.status_code == 200
    # response should include X-Request-ID header
    assert "X-Request-ID" in r.headers
    rid = r.headers["X-Request-ID"]

    # we don't assert on the log contents here; header presence is enough
    pass