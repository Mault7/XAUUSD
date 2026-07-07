from pathlib import Path


def test_structure_route_is_registered() -> None:
    app_module = Path("backend/api/http/app.py").read_text(encoding="utf-8")

    assert "structure_router" in app_module
    assert '"/structure"' in Path("backend/api/http/routes/structure.py").read_text(
        encoding="utf-8"
    )

