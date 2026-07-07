from pydantic import BaseModel

from backend.api.schemas.indicators import IndicatorValueSchema
from backend.api.schemas.structure import (
    StructureEventSchema,
    StructureLevelSchema,
    SwingPointSchema,
)


class DashboardRiskSchema(BaseModel):
    direction: str
    entry: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    risk_percent: float
    lot_size: float
    risk_reward: float
    explanation: str


class DashboardScoreFactorSchema(BaseModel):
    name: str
    score: float
    weight: float
    explanation: str


class DashboardAlertSchema(BaseModel):
    eligible: bool
    channel: str
    confidence: float
    threshold: float
    suppressed: bool
    message: str


class AssetDashboardOverviewSchema(BaseModel):
    symbol: str
    timeframe: str
    provider: str
    candles_loaded: int
    last_close: float | None
    trend_bias: str
    indicators: list[IndicatorValueSchema]
    swing_highs: list[SwingPointSchema]
    swing_lows: list[SwingPointSchema]
    support_levels: list[StructureLevelSchema]
    resistance_levels: list[StructureLevelSchema]
    structure_events: list[StructureEventSchema]
    risk: DashboardRiskSchema
    total_score: float
    confidence: float
    threshold: float
    suppressed: bool
    reasons: list[str]
    score_factors: list[DashboardScoreFactorSchema]
    alert: DashboardAlertSchema

