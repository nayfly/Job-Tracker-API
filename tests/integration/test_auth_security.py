import os
import uuid

# make sure config will choose the in-memory database
os.environ.setdefault("ENV", "test")

from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token


def create_user_and_token(client, email=None):
    email = email or f"u-{uuid.uuid4().hex[:8]}@x.com"
    password = "pass1234"
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201
    r = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    return email, r.json()["access_token"]


def test_access_without_token():
    client = TestClient(app)
    r = client.get("/companies/")
    assert r.status_code == 401


def test_invalid_token():
    client = TestClient(app)
    headers = {"Authorization": "Bearer invalid.token.here"}
    r = client.get("/companies/", headers=headers)
    assert r.status_code == 401


def test_expired_token():
    # craft a token which already expired by setting negative expiry
    token = create_access_token("nobody@example.com", expires_minutes=-5)
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/companies/", headers=headers)
    assert r.status_code == 401


def test_login_rate_limit():
    client = TestClient(app)
    email = f"rl-{uuid.uuid4().hex[:8]}@x.com"
    # create account
    r = client.post("/auth/register", json={"email": email, "password": "pass1234"})
    assert r.status_code == 201
    # make several bad attempts
    for _ in range(6):
        r = client.post(
            "/auth/login",
            data={"username": email, "password": "wrong"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    # after exceeding threshold should get 429
    assert r.status_code == 429
