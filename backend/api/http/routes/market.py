from fastapi import APIRouter

from backend.api.dependencies.container import get_container
from backend.api.schemas.market import AssetMarketStatusResponse, MarketOverviewResponse

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/overview", response_model=MarketOverviewResponse)
def get_market_overview() -> MarketOverviewResponse:
    container = get_container()
    statuses = container.market_data_service.get_asset_statuses()
    return MarketOverviewResponse(
        provider=container.market_data_provider.provider_name,
        assets=[AssetMarketStatusResponse.model_validate(status.model_dump()) for status in statuses],
    )

