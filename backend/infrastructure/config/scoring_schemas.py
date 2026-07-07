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


class ScoringConfig(BaseModel):
    weights: ScoringWeights
    defaults: ScoringDefaults

