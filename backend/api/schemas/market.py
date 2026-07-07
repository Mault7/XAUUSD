from pydantic import BaseModel


class AssetMarketStatusResponse(BaseModel):
    symbol: str
    timeframe: str | None
    provider: str
    available: bool
    candles_loaded: int
    last_close: float | None
    message: str


class MarketOverviewResponse(BaseModel):
    provider: str
    assets: list[AssetMarketStatusResponse]

