from fastapi.testclient import TestClient

from backend.main import app


def test_healthcheck_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "XAUUSD" in response.json()["assets"]
    assert response.json()["market_provider"] == "memory"

