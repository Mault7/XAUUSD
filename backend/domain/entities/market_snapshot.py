from dataclasses import dataclass
from datetime import datetime

from backend.domain.entities.candle import Candle
from backend.domain.value_objects.timeframe import Timeframe


@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    timeframe: Timeframe
    source: str
    fetched_at: datetime
    candles: list[Candle]

