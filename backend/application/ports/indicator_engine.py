from abc import ABC, abstractmethod

from backend.domain.entities.indicator_snapshot import IndicatorSnapshot
from backend.domain.entities.market_snapshot import MarketSnapshot


class IndicatorEngine(ABC):
    @abstractmethod
    def analyze(self, snapshot: MarketSnapshot) -> list[IndicatorSnapshot]:
        """Compute indicator snapshots for normalized market data."""

