from backend.application.ports.alert_formatter import AlertFormatter
from backend.domain.entities.alert_message import AlertMessage
from backend.domain.entities.risk_plan import RiskPlan
from backend.domain.entities.score_breakdown import ScoreBreakdown
from backend.domain.entities.structure_snapshot import StructureSnapshot


class TelegramAlertFormatter(AlertFormatter):
    def format_message(
        self,
        symbol: str,
        score_breakdown: ScoreBreakdown,
        risk_plan: RiskPlan,
        structure: StructureSnapshot,
    ) -> AlertMessage:
        direction = risk_plan.direction.value.upper()
        trend = structure.trend_bias.value.capitalize()
        reasons = score_breakdown.reasons[:5] or ["Multi-factor conditions are being evaluated."]
        body = "\n".join(
            [
                f"Asset: {symbol}",
                f"Direction: {direction}",
                f"Confidence: {score_breakdown.confidence:.2f}%",
                f"Trend: {trend}",
                "",
                "Reasons",
                *[f"- {reason}" for reason in reasons],
                "",
                "Entry",
                f"{risk_plan.entry:.4f}",
                "",
                "Stop Loss",
                f"{risk_plan.stop_loss:.4f}",
                "",
                "Take Profit",
                f"TP1: {risk_plan.take_profit_1:.4f}",
                f"TP2: {risk_plan.take_profit_2:.4f}",
                f"TP3: {risk_plan.take_profit_3:.4f}",
                "",
                "Risk Reward",
                f"{risk_plan.risk_reward:.2f}",
            ]
        )
        return AlertMessage(
            channel="telegram",
            subject=f"{symbol} {direction} {score_breakdown.confidence:.2f}%",
            body=body,
            asset=symbol,
            confidence=score_breakdown.confidence,
        )

