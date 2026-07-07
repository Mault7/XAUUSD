from abc import ABC, abstractmethod

from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.entities.structure_snapshot import StructureSnapshot


class StructureEngine(ABC):
    @abstractmethod
    def analyze(self, snapshot: MarketSnapshot) -> StructureSnapshot:
        """Detect market structure from a normalized market snapshot."""

