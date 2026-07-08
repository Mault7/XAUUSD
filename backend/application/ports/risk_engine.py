from abc import ABC, abstractmethod

from backend.domain.entities.indicator_snapshot import IndicatorSnapshot
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.entities.risk_plan import RiskPlan
from backend.domain.entities.symbol_spec import SymbolSpec
from backend.domain.entities.structure_snapshot import StructureSnapshot


class RiskEngine(ABC):
    @abstractmethod
    def build_plan(
        self,
        snapshot: MarketSnapshot,
        symbol_spec: SymbolSpec,
        indicators: list[IndicatorSnapshot],
        structure: StructureSnapshot,
        risk_percent: float,
        account_size: float,
    ) -> RiskPlan:
        """Create an explainable advisory risk plan."""
