from pathlib import Path


def test_dashboard_service_exists_and_is_wired() -> None:
    service_module = Path("backend/application/services/dashboard_service.py").read_text(
        encoding="utf-8"
    )
    container_module = Path("backend/api/dependencies/container.py").read_text(encoding="utf-8")

    assert "class DashboardService" in service_module
    assert "self.dashboard_service" in container_module

