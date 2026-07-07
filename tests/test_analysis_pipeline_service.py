from pathlib import Path


def test_analysis_pipeline_service_is_shared_dependency() -> None:
    pipeline_module = Path("backend/application/services/analysis_pipeline_service.py").read_text(
        encoding="utf-8"
    )
    container_module = Path("backend/api/dependencies/container.py").read_text(encoding="utf-8")

    assert "class AnalysisPipelineService" in pipeline_module
    assert "self.analysis_pipeline_service" in container_module
