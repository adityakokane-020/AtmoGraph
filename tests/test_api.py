from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


def test_home():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Welcome to AtmoGraph API"
    assert data["status"] == "Running"


def test_graph():
    response = client.get("/graph")

    assert response.status_code == 200

    data = response.json()

    assert "nodes" in data
    assert "relationships" in data


def test_ripple_effect_not_found():
    response = client.get("/ripple-effect/Earthquake")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Disruption not found"
    }
    