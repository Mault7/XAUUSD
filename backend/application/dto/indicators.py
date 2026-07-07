from pydantic import BaseModel


class IndicatorValueResponse(BaseModel):
    name: str
    value: float
    direction: str
    strength: float
    explanation: str


class AssetIndicatorOverviewResponse(BaseModel):
    symbol: str
    timeframe: str
    provider: str
    indicators: list[IndicatorValueResponse]

