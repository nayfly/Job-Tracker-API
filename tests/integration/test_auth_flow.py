# tests/integration/test_auth_flow.py
import os
import uuid

# make sure config will choose the in-memory database
os.environ.setdefault("ENV", "test")

from fastapi.testclient import TestClient

from app.main import app


def test_register_login_flow():
    client = TestClient(app)
    email = f"a-{uuid.uuid4().hex[:8]}@a.com"

    r = client.post("/auth/register", json={"email": email, "password": "pass1234"})
    assert r.status_code == 201

    r = client.post(
        "/auth/login",
        data={"username": email, "password": "pass1234"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
