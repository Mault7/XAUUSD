from pathlib import Path


def test_indicator_route_is_registered() -> None:
    app_module = Path("backend/api/http/app.py").read_text(encoding="utf-8")

    assert "indicators_router" in app_module
    assert '"/indicators"' in Path("backend/api/http/routes/indicators.py").read_text(
        encoding="utf-8"
    )

