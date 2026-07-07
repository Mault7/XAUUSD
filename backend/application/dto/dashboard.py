from pydantic import BaseModel

from backend.application.dto.indicators import IndicatorValueResponse
from backend.application.dto.structure import (
    StructureEventResponse,
    StructureLevelResponse,
    SwingPointResponse,
)


class DashboardRiskResponse(BaseModel):
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


class DashboardScoreFactorResponse(BaseModel):
    name: str
    score: float
    weight: float
    explanation: str


class DashboardAlertResponse(BaseModel):
    eligible: bool
    channel: str
    confidence: float
    threshold: float
    suppressed: bool
    message: str


class AssetDashboardOverviewResponse(BaseModel):
    symbol: str
    timeframe: str
    provider: str
    candles_loaded: int
    last_close: float | None
    trend_bias: str
    indicators: list[IndicatorValueResponse]
    swing_highs: list[SwingPointResponse]
    swing_lows: list[SwingPointResponse]
    support_levels: list[StructureLevelResponse]
    resistance_levels: list[StructureLevelResponse]
    structure_events: list[StructureEventResponse]
    risk: DashboardRiskResponse
    total_score: float
    confidence: float
    threshold: float
    suppressed: bool
    reasons: list[str]
    score_factors: list[DashboardScoreFactorResponse]
    alert: DashboardAlertResponse

