from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["version"] == "2.0.0"


def test_system_discovery():
    response = client.get("/api/systems")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] >= 1
    assert "systems" in data
    assert "jira" in data["systems"]


def test_stats_endpoint():
    response = client.get("/api/stats")

    assert response.status_code == 200

    data = response.json()

    assert data["systems_available"] >= 1
    assert "users_tracked" in data
    assert "tickets_open" in data
    assert "incidents_open" in data
    assert "access_requests_pending" in data


def test_user_access_check_specific_system():
    response = client.get("/api/users/janesmith/access?system=jira")

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "janesmith"
    assert data["systems_checked"] == 1
    assert "access_found" in data


def test_invalid_system_returns_404():
    response = client.get("/api/users/janesmith/access?system=notarealsystem")

    assert response.status_code == 404


def test_grant_access_mock_mode():
    response = client.post("/api/users/testapi/grant/jira?mock=true")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["username"] == "testapi"
    assert data["system"] == "jira"
    assert data["action"] == "grant"
    assert data["mock"] is True


def test_remove_access_dry_run():
    response = client.post("/api/users/testapi/remove/jira?mock=true&dry_run=true")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["username"] == "testapi"
    assert data["system"] == "jira"
    assert data["action"] == "remove"
    assert data["dry_run"] is True