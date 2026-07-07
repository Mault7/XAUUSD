from pydantic import BaseModel


class SwingPointResponse(BaseModel):
    kind: str
    price: float
    index: int
    label: str


class StructureLevelResponse(BaseModel):
    kind: str
    price: float
    explanation: str


class StructureEventResponse(BaseModel):
    name: str
    direction: str
    strength: float
    explanation: str


class AssetStructureOverviewResponse(BaseModel):
    symbol: str
    timeframe: str
    provider: str
    trend_bias: str
    swing_highs: list[SwingPointResponse]
    swing_lows: list[SwingPointResponse]
    support_levels: list[StructureLevelResponse]
    resistance_levels: list[StructureLevelResponse]
    events: list[StructureEventResponse]

