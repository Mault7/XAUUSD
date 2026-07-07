from fastapi import APIRouter

from backend.api.dependencies.container import get_container
from backend.api.schemas.indicators import AssetIndicatorOverviewSchema

router = APIRouter(prefix="/indicators", tags=["indicators"])


@router.get("/overview", response_model=list[AssetIndicatorOverviewSchema])
def get_indicator_overview() -> list[AssetIndicatorOverviewSchema]:
    container = get_container()
    overview = container.indicator_service.get_indicator_overview()
    return [
        AssetIndicatorOverviewSchema.model_validate(item.model_dump())
        for item in overview
    ]

