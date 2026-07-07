from pydantic import BaseModel


class AssetMarketStatus(BaseModel):
    symbol: str
    timeframe: str | None
    provider: str
    available: bool
    candles_loaded: int
    last_close: float | None
    message: str

