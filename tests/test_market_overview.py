from fastapi.testclient import TestClient

from backend.main import app


def test_market_overview_uses_fallback_provider() -> None:
    client = TestClient(app)

    response = client.get("/market/overview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "memory"
    assert payload["assets"][0]["available"] is True
    assert payload["assets"][0]["candles_loaded"] == 200
