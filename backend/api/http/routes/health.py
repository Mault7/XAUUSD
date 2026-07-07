from fastapi import APIRouter

from backend.api.dependencies.container import get_container
from backend.api.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    container = get_container()
    summary = container.analysis_service.get_supported_assets_summary()
    return HealthResponse(
        status="ok",
        environment=container.settings.app_env,
        assets=summary,
        market_provider=container.analysis_service.get_market_provider_name(),
    )
