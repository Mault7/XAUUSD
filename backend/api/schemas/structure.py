from pydantic import BaseModel


class SwingPointSchema(BaseModel):
    kind: str
    price: float
    index: int
    label: str


class StructureLevelSchema(BaseModel):
    kind: str
    price: float
    explanation: str


class StructureEventSchema(BaseModel):
    name: str
    direction: str
    strength: float
    explanation: str


class AssetStructureOverviewSchema(BaseModel):
    symbol: str
    timeframe: str
    provider: str
    trend_bias: str
    swing_highs: list[SwingPointSchema]
    swing_lows: list[SwingPointSchema]
    support_levels: list[StructureLevelSchema]
    resistance_levels: list[StructureLevelSchema]
    events: list[StructureEventSchema]

