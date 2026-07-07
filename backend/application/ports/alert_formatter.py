from abc import ABC, abstractmethod

from backend.domain.entities.alert_message import AlertMessage
from backend.domain.entities.risk_plan import RiskPlan
from backend.domain.entities.score_breakdown import ScoreBreakdown
from backend.domain.entities.structure_snapshot import StructureSnapshot


class AlertFormatter(ABC):
    @abstractmethod
    def format_message(
        self,
        symbol: str,
        score_breakdown: ScoreBreakdown,
        risk_plan: RiskPlan,
        structure: StructureSnapshot,
    ) -> AlertMessage:
        """Create a human-readable alert payload."""

