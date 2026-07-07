from datetime import UTC, datetime, timedelta

from backend.domain.entities.candle import Candle
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.value_objects.timeframe import Timeframe
from backend.infrastructure.config.scoring_loader import ScoringConfigLoader
from backend.infrastructure.indicators.engine import DefaultIndicatorEngine
from backend.infrastructure.risk.engine import DefaultRiskEngine
from backend.infrastructure.scoring.engine import DefaultScoringEngine
from backend.infrastructure.structure.engine import DefaultStructureEngine


def test_scoring_engine_returns_weighted_breakdown() -> None:
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
    risk_plan = DefaultRiskEngine().build_plan(snapshot, indicators, structure, 1.0, 10000.0)

    breakdown = DefaultScoringEngine(ScoringConfigLoader("config/scoring.yaml")).score(
        snapshot, indicators, structure, risk_plan, threshold=75.0
    )

    assert breakdown.total_score > 0
    assert breakdown.factors
    assert any(factor.name == "trend_alignment" for factor in breakdown.factors)

