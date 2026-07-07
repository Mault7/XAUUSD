from fastapi import APIRouter

from backend.api.dependencies.container import get_container
from backend.api.schemas.risk import RiskPlanSchema

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/overview", response_model=list[RiskPlanSchema])
def get_risk_overview() -> list[RiskPlanSchema]:
    container = get_container()
    overview = container.risk_service.get_risk_overview()
    return [RiskPlanSchema.model_validate(item.model_dump()) for item in overview]

