from pydantic import BaseModel, Field


class ScoringWeights(BaseModel):
    trend_alignment: float = Field(ge=0)
    structure: float = Field(ge=0)
    support_resistance: float = Field(ge=0)
    rsi: float = Field(ge=0)
    atr: float = Field(ge=0)
    macd: float = Field(ge=0)
    adx: float = Field(ge=0)
    volume: float = Field(ge=0)
    smart_money: float = Field(ge=0)
    news_filter: float = Field(ge=0)


class ScoringDefaults(BaseModel):
    signal_threshold: float = Field(ge=0, le=100)
    suppression_floor: float = Field(ge=0, le=100)


class AlertingConfig(BaseModel):
    scan_interval_seconds: int = Field(ge=10)
    cooldown_minutes: int = Field(ge=0)
    symbol_cooldown_minutes: int = Field(ge=0)
    preferred_timeframe: str = Field(min_length=2)
    context_timeframes: list[str] = Field(default_factory=list)
    min_risk_reward: float = Field(ge=0)
    min_adx_strength: float = Field(ge=0, le=1)
    min_atr_strength: float = Field(ge=0, le=1)
    min_volume_strength: float = Field(ge=0, le=1)
    min_trend_alignment_strength: float = Field(ge=0, le=1)
    min_structure_strength: float = Field(ge=0, le=1)


class ScoringConfig(BaseModel):
    weights: ScoringWeights
    defaults: ScoringDefaults
    alerting: AlertingConfig
