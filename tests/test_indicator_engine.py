from datetime import UTC, datetime, timedelta

from backend.domain.entities.candle import Candle
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.value_objects.timeframe import Timeframe
from backend.infrastructure.indicators.engine import DefaultIndicatorEngine


def test_indicator_engine_returns_expected_indicator_set() -> None:
    now = datetime.now(UTC)
    candles = [
        Candle(
            timestamp=now - timedelta(minutes=5 * (250 - index)),
            open=100.0 + index * 0.1,
            high=100.4 + index * 0.1,
            low=99.8 + index * 0.1,
            close=100.2 + index * 0.1,
            volume=1000 + index * 5,
        )
        for index in range(250)
    ]
    snapshot = MarketSnapshot(
        symbol="XAUUSD",
        timeframe=Timeframe.M5,
        source="memory",
        fetched_at=now,
        candles=candles,
    )

    indicators = DefaultIndicatorEngine().analyze(snapshot)

    assert len(indicators) == 11
    assert {indicator.name for indicator in indicators} == {
        "EMA20",
        "EMA50",
        "EMA100",
        "EMA200",
        "RSI",
        "ATR",
        "MACD",
        "ADX",
        "BollingerBands",
        "VWAP",
        "Volume",
    }

