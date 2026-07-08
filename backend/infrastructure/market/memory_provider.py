from datetime import UTC, datetime, timedelta

from backend.application.ports.market_data import MarketDataProvider
from backend.domain.entities.candle import Candle
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.entities.symbol_spec import SymbolSpec
from backend.domain.value_objects.timeframe import Timeframe


class MemoryMarketDataProvider(MarketDataProvider):
    """Deterministic fallback provider for local development and tests."""

    @property
    def provider_name(self) -> str:
        return "memory"

    def is_available(self) -> bool:
        return True

    def get_market_snapshot(
        self, symbol: str, timeframe: Timeframe, candles_limit: int = 200
    ) -> MarketSnapshot:
        now = datetime.now(UTC)
        candles = [
            Candle(
                timestamp=now - timedelta(minutes=(candles_limit - index) * 5),
                open=100.0 + index,
                high=100.5 + index,
                low=99.5 + index,
                close=100.2 + index,
                volume=1000 + index * 10,
            )
            for index in range(candles_limit)
        ]
        return MarketSnapshot(
            symbol=symbol,
            timeframe=timeframe,
            source=self.provider_name,
            fetched_at=now,
            candles=candles,
        )

    def get_symbol_spec(self, symbol: str) -> SymbolSpec:
        return SymbolSpec(
            symbol=symbol,
            point=0.01,
            tick_size=0.01,
            tick_value=1.0,
            contract_size=100.0,
            volume_min=0.01,
            volume_step=0.01,
            volume_max=100.0,
        )
