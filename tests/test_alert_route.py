from pathlib import Path


def test_alert_route_is_registered() -> None:
    app_module = Path("backend/api/http/app.py").read_text(encoding="utf-8")

    assert "alerts_router" in app_module
    route_module = Path("backend/api/http/routes/alerts.py").read_text(encoding="utf-8")
    assert '"/alerts"' in route_module
    assert '"/dispatch"' in route_module
