from pathlib import Path


def test_dashboard_route_is_registered() -> None:
    app_module = Path("backend/api/http/app.py").read_text(encoding="utf-8")

    assert "dashboard_router" in app_module
    route_module = Path("backend/api/http/routes/dashboard.py").read_text(encoding="utf-8")
    assert '"/dashboard"' in route_module

