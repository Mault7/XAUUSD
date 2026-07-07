from fastapi import APIRouter

from backend.api.dependencies.container import get_container
from backend.api.schemas.scoring import AssetScoreOverviewSchema

router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.get("/overview", response_model=list[AssetScoreOverviewSchema])
def get_scoring_overview() -> list[AssetScoreOverviewSchema]:
    container = get_container()
    overview = container.scoring_service.get_scoring_overview()
    return [AssetScoreOverviewSchema.model_validate(item.model_dump()) for item in overview]

