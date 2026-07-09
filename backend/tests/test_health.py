from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_status_code():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_structure():
    response = client.get("/health")
    data = response.json()
    assert "status" in data
    assert "classification_model_loaded" in data
    assert "regression_model_loaded" in data
    assert data["status"] == "ok"
