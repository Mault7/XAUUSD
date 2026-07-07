from datetime import UTC, datetime, timedelta

from backend.domain.entities.candle import Candle
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.value_objects.timeframe import Timeframe
from backend.infrastructure.indicators.engine import DefaultIndicatorEngine
from backend.infrastructure.risk.engine import DefaultRiskEngine
from backend.infrastructure.structure.engine import DefaultStructureEngine


def test_risk_engine_returns_advisory_plan() -> None:
    now = datetime.now(UTC)
    closes = [100 + index * 0.35 + ((-1) ** index) * 0.8 for index in range(250)]
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
    indicators = DefaultIndicatorEngine().analyze(snapshot)
    structure = DefaultStructureEngine().analyze(snapshot)

    plan = DefaultRiskEngine().build_plan(snapshot, indicators, structure, 1.0, 10000.0)

    assert plan.entry > 0
    assert plan.stop_loss > 0
    assert plan.take_profit_1 > 0
    assert plan.risk_reward > 0
    assert plan.lot_size > 0
