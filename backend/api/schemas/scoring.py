from pydantic import BaseModel


class ScoreFactorSchema(BaseModel):
    name: str
    score: float
    weight: float
    explanation: str


class AssetScoreOverviewSchema(BaseModel):
    symbol: str
    timeframe: str
    provider: str
    total_score: float
    confidence: float
    threshold: float
    suppressed: bool
    reasons: list[str]
    factors: list[ScoreFactorSchema]

