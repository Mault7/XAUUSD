from backend.domain.entities.risk_plan import RiskPlan
from backend.domain.entities.score_breakdown import ScoreBreakdown
from backend.domain.entities.structure_snapshot import StructureSnapshot
from backend.domain.value_objects.signal_direction import SignalDirection
from backend.infrastructure.alerts.formatter import TelegramAlertFormatter


def test_alert_formatter_builds_explainable_message() -> None:
    formatter = TelegramAlertFormatter()
    message = formatter.format_message(
        symbol="XAUUSD",
        score_breakdown=ScoreBreakdown(
            total_score=82.0,
            confidence=82.0,
            threshold=75.0,
            suppressed=False,
            reasons=["Trend alignment is strong.", "Volume is supportive."],
            factors=[],
        ),
        risk_plan=RiskPlan(
            direction=SignalDirection.BULLISH,
            entry=2350.0,
            stop_loss=2338.0,
            take_profit_1=2362.0,
            take_profit_2=2374.0,
            take_profit_3=2386.0,
            risk_percent=1.0,
            lot_size=0.5,
            risk_reward=2.0,
            explanation="Risk derived from support and ATR.",
        ),
        structure=StructureSnapshot(
            trend_bias=SignalDirection.BULLISH,
            swing_highs=[],
            swing_lows=[],
            support_levels=[],
            resistance_levels=[],
            events=[],
        ),
    )

    assert "Asset: XAUUSD" in message.body
    assert "Confidence: 82.00%" in message.body
    assert "TP2: 2374.0000" in message.body

