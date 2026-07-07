from datetime import UTC, datetime, timedelta

from backend.domain.entities.candle import Candle
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.value_objects.signal_direction import SignalDirection
from backend.domain.value_objects.timeframe import Timeframe
from backend.infrastructure.structure.engine import DefaultStructureEngine


def test_structure_engine_detects_swing_points_and_levels() -> None:
    now = datetime.now(UTC)
    closes = [108, 106, 104, 110, 107, 103, 109, 106, 102, 111, 108, 104, 112, 109, 105, 113, 110]
    candles = [
        Candle(
            timestamp=now - timedelta(minutes=5 * (len(closes) - index)),
            open=value - 0.2,
            high=value + 0.4,
            low=value - 0.6,
            close=value,
            volume=1000 + index * 10,
        )
        for index, value in enumerate(closes)
    ]
    snapshot = MarketSnapshot(
        symbol="XAUUSD",
        timeframe=Timeframe.M5,
        source="memory",
        fetched_at=now,
        candles=candles,
    )

    structure = DefaultStructureEngine().analyze(snapshot)

    assert structure.trend_bias in {
        SignalDirection.BULLISH,
        SignalDirection.BEARISH,
        SignalDirection.SIDEWAYS,
    }
    assert structure.swing_highs
    assert structure.swing_lows
    assert structure.support_levels
    assert structure.resistance_levels
    assert structure.events
