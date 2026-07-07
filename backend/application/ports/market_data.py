from abc import ABC, abstractmethod

from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.value_objects.timeframe import Timeframe


class MarketDataProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return whether the provider can serve market data."""

    @abstractmethod
    def get_market_snapshot(
        self, symbol: str, timeframe: Timeframe, candles_limit: int = 200
    ) -> MarketSnapshot:
        """Return normalized candle data for a symbol and timeframe."""

