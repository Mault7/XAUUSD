from fastapi import APIRouter

from backend.api.dependencies.container import get_container
from backend.api.schemas.structure import AssetStructureOverviewSchema

router = APIRouter(prefix="/structure", tags=["structure"])


@router.get("/overview", response_model=list[AssetStructureOverviewSchema])
def get_structure_overview() -> list[AssetStructureOverviewSchema]:
    container = get_container()
    overview = container.structure_service.get_structure_overview()
    return [AssetStructureOverviewSchema.model_validate(item.model_dump()) for item in overview]

