from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreFactor:
    name: str
    score: float
    weight: float
    explanation: str


@dataclass(frozen=True)
class ScoreBreakdown:
    total_score: float
    confidence: float
    threshold: float
    suppressed: bool
    reasons: list[str]
    factors: list[ScoreFactor]

