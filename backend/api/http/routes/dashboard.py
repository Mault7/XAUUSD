from fastapi import APIRouter

from backend.api.dependencies.container import get_container
from backend.api.schemas.dashboard import AssetDashboardOverviewSchema

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=list[AssetDashboardOverviewSchema])
def get_dashboard_overview() -> list[AssetDashboardOverviewSchema]:
    container = get_container()
    overview = container.dashboard_service.get_overview()
    return [AssetDashboardOverviewSchema.model_validate(item.model_dump()) for item in overview]

