from pydantic import BaseModel


class IndicatorValueSchema(BaseModel):
    name: str
    value: float
    direction: str
    strength: float
    explanation: str


class AssetIndicatorOverviewSchema(BaseModel):
    symbol: str
    timeframe: str
    provider: str
    indicators: list[IndicatorValueSchema]

