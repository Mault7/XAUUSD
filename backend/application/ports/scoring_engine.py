from abc import ABC, abstractmethod

from backend.domain.entities.indicator_snapshot import IndicatorSnapshot
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.entities.risk_plan import RiskPlan
from backend.domain.entities.score_breakdown import ScoreBreakdown
from backend.domain.entities.structure_snapshot import StructureSnapshot


class ScoringEngine(ABC):
    @abstractmethod
    def score(
        self,
        snapshot: MarketSnapshot,
        indicators: list[IndicatorSnapshot],
        structure: StructureSnapshot,
        risk_plan: RiskPlan,
        threshold: float,
    ) -> ScoreBreakdown:
        """Return a weighted and explainable opportunity score."""

