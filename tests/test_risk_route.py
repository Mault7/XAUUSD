from pathlib import Path


def test_risk_route_is_registered() -> None:
    app_module = Path("backend/api/http/app.py").read_text(encoding="utf-8")

    assert "risk_router" in app_module
    assert '"/risk"' in Path("backend/api/http/routes/risk.py").read_text(encoding="utf-8")

