from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "N": 90,
    "P": 42,
    "K": 43,
    "temperature": 20.87,
    "humidity": 82.0,
    "ph": 6.5,
    "rainfall": 202.9,
}


def test_recommend_crop_valid_payload():
    response = client.post("/recommend_crop", json=VALID_PAYLOAD)
    # 200 si le modèle MLflow est chargé, 503 sinon (ex: registry vide en local)
    assert response.status_code in (200, 503)
    if response.status_code == 200:
        data = response.json()
        assert "recommended_crop" in data
        assert "confidence" in data


def test_recommend_crop_missing_field():
    payload = VALID_PAYLOAD.copy()
    del payload["N"]
    response = client.post("/recommend_crop", json=payload)
    assert response.status_code == 422


def test_recommend_crop_invalid_ph():
    payload = VALID_PAYLOAD.copy()
    payload["ph"] = 25  # hors bornes (0-14)
    response = client.post("/recommend_crop", json=payload)
    assert response.status_code == 422
