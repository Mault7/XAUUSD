from fastapi import APIRouter

from backend.api.dependencies.container import get_container
from backend.api.schemas.alerts import AlertDispatchSchema, AlertPreviewSchema

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/preview", response_model=list[AlertPreviewSchema])
def preview_alerts() -> list[AlertPreviewSchema]:
    container = get_container()
    overview = container.alert_service.preview_alerts()
    return [AlertPreviewSchema.model_validate(item.model_dump()) for item in overview]


@router.post("/dispatch", response_model=list[AlertDispatchSchema])
def dispatch_alerts() -> list[AlertDispatchSchema]:
    container = get_container()
    overview = container.alert_service.dispatch_alerts()
    return [AlertDispatchSchema.model_validate(item.model_dump()) for item in overview]

