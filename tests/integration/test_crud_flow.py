import os
import uuid

from fastapi.testclient import TestClient

from app.main import app

# ensure test settings are used before the application is imported
os.environ.setdefault("ENV", "test")


def register_and_login(client: TestClient) -> str:
    email = f"b-{uuid.uuid4().hex[:8]}@example.com"
    pwd = "password123"
    r = client.post("/auth/register", json={"email": email, "password": pwd})
    assert r.status_code == 201
    r = client.post(
        "/auth/login",
        data={"username": email, "password": pwd},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    return r.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_companies_applications_followups_flow():
    client = TestClient(app)
    token = register_and_login(client)

    # create company
    r = client.post(
        "/companies/",
        json={"name": "Acme Corp", "website": "https://acme.example"},
        headers=auth_header(token),
    )
    assert r.status_code == 201
    company = r.json()
    assert company["name"] == "Acme Corp"

    # list companies
    r = client.get("/companies/", headers=auth_header(token))
    assert r.status_code == 200
    assert len(r.json()) == 1

    # create application for the company
    r = client.post(
        "/applications/",
        json={"position": "Engineer", "company_id": company["id"]},
        headers=auth_header(token),
    )
    assert r.status_code == 201
    application = r.json()
    assert application["position"] == "Engineer"

    # list applications
    r = client.get("/applications/", headers=auth_header(token))
    assert r.status_code == 200
    assert len(r.json()) == 1

    # filtering and ordering should respect query params (status, company_id)
    r = client.get(
        "/applications/",
        params={"status": "applied", "company_id": company["id"], "limit": 5, "order_by": "id"},
        headers=auth_header(token),
    )
    assert r.status_code == 200
    assert len(r.json()) == 1

    # patch the application to change status
    r = client.patch(
        f"/applications/{application['id']}",
        json={"status": "interview"},
        headers=auth_header(token),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "interview"

    # add a followup
    r = client.post(
        "/followups/",
        json={"application_id": application["id"], "note": "Sent resume"},
        headers=auth_header(token),
    )
    assert r.status_code == 201
    followup = r.json()
    assert followup["note"] == "Sent resume"

    # list followups for application
    r = client.get(
        "/followups/",
        params={"application_id": application["id"]},
        headers=auth_header(token),
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["note"] == "Sent resume"

    # dashboard summary should reflect one application and one followup
    r = client.get("/applications/dashboard/summary", headers=auth_header(token))
    assert r.status_code == 200
    summary = r.json()
    # after patch the application status was changed to interview
    assert summary["counts_by_status"].get("interview", 0) == 1
    assert len(summary["recent_followups"]) == 1

    # delete the followup
    r = client.delete(f"/followups/{data[0]['id']}", headers=auth_header(token))
    assert r.status_code == 204

    # followups list should now be empty
    r = client.get(
        "/followups/",
        params={"application_id": application["id"]},
        headers=auth_header(token),
    )
    assert r.status_code == 200
    assert r.json() == []

    # delete application
    r = client.delete(f"/applications/{application['id']}", headers=auth_header(token))
    assert r.status_code == 204

    # applications list should now be empty
    r = client.get("/applications/", headers=auth_header(token))
    assert r.status_code == 200
    assert r.json() == []

    # invalid application (future date)
    from datetime import date, timedelta
    future = date.today() + timedelta(days=1)
    r = client.post(
        "/applications/",
        json={"position": "Future job", "company_id": company["id"], "applied_at": future.isoformat()},
        headers=auth_header(token),
    )
    assert r.status_code == 422

    # invalid followup (empty note)
    r = client.post(
        "/followups/",
        json={"application_id": application["id"], "note": "   "},
        headers=auth_header(token),
    )
    assert r.status_code == 422
