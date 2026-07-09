from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

VALID_PAYLOAD = {"area": "Morocco", "item": "Wheat", "year": 2020}


def test_predict_yield_valid_payload():
    response = client.post("/predict_yield", json=VALID_PAYLOAD)
    assert response.status_code in (200, 503)
    if response.status_code == 200:
        data = response.json()
        assert "predicted_yield_tha" in data


def test_predict_yield_missing_field():
    payload = VALID_PAYLOAD.copy()
    del payload["item"]
    response = client.post("/predict_yield", json=payload)
    assert response.status_code == 422


def test_predict_yield_invalid_year():
    payload = VALID_PAYLOAD.copy()
    payload["year"] = 1800  # hors bornes (1961-2030)
    response = client.post("/predict_yield", json=payload)
    assert response.status_code == 422
