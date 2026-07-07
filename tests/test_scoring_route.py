from pathlib import Path


def test_scoring_route_is_registered() -> None:
    app_module = Path("backend/api/http/app.py").read_text(encoding="utf-8")

    assert "scoring_router" in app_module
    assert '"/scoring"' in Path("backend/api/http/routes/scoring.py").read_text(encoding="utf-8")

