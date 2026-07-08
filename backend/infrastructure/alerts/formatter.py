from datetime import UTC

from backend.application.ports.alert_formatter import AlertFormatter
from backend.domain.entities.alert_message import AlertMessage
from backend.domain.entities.indicator_snapshot import IndicatorSnapshot
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.entities.risk_plan import RiskPlan
from backend.domain.entities.score_breakdown import ScoreBreakdown
from backend.domain.entities.structure_snapshot import StructureSnapshot


class TelegramAlertFormatter(AlertFormatter):
    def format_message(
        self,
        symbol: str,
        timeframe: str,
        snapshot: MarketSnapshot,
        indicators: list[IndicatorSnapshot],
        score_breakdown: ScoreBreakdown,
        risk_plan: RiskPlan,
        structure: StructureSnapshot,
    ) -> AlertMessage:
        direction = _translate_direction(risk_plan.direction.value)
        trend = _translate_direction(structure.trend_bias.value)
        operation = "COMPRA" if direction == "ALCISTA" else "VENTA"
        summary = _summary_label(direction, score_breakdown.confidence)
        reasons = score_breakdown.reasons[:5] or ["Las condiciones multifactor todavía se están evaluando."]
        rsi = _find_indicator(indicators, "RSI")
        atr = _find_indicator(indicators, "ATR")
        adx = _find_indicator(indicators, "ADX")
        timestamp = snapshot.fetched_at.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        body = "\n".join(
            [
                f"ALERTA {operation} | {symbol} | {timeframe}",
                f"Fecha y hora: {timestamp}",
                "",
                "Resumen rapido",
                f"- Estado: {summary}",
                f"- Direccion: {direction}",
                f"- Tendencia: {trend}",
                f"- Confianza: {score_breakdown.confidence:.2f}%",
                "",
                "Plan operativo",
                f"- Entrada: {risk_plan.entry:.4f}",
                f"- Stop Loss: {risk_plan.stop_loss:.4f}",
                f"- Take Profit 1: {risk_plan.take_profit_1:.4f}",
                f"- Take Profit 2: {risk_plan.take_profit_2:.4f}",
                f"- Take Profit 3: {risk_plan.take_profit_3:.4f}",
                "",
                "Indicadores clave",
                f"- RSI: {_format_indicator_value(rsi, 2)}",
                f"- ATR: {_format_indicator_value(atr, 4)}",
                f"- ADX: {_format_indicator_value(adx, 2)}",
                "",
                "Por que se detecto",
                *[f"- {reason}" for reason in reasons],
                "",
                "Gestion de riesgo",
                f"- Lote: {risk_plan.lot_size:.2f}",
                f"- Perdida estimada: {risk_plan.risk_amount:.2f} USD",
                f"- Riesgo/Beneficio: {risk_plan.risk_reward:.2f}",
                "",
                "Lectura rapida",
                f"- Activo: {symbol}",
                f"- Temporalidad: {timeframe}",
                f"- Tipo de operacion: {operation}",
            ]
        )
        return AlertMessage(
            channel="telegram",
            subject=f"{symbol} {timeframe} {operation} {score_breakdown.confidence:.2f}%",
            body=body,
            asset=symbol,
            confidence=score_breakdown.confidence,
        )


def _translate_direction(direction: str) -> str:
    mapping = {
        "bullish": "ALCISTA",
        "bearish": "BAJISTA",
        "sideways": "LATERAL",
        "neutral": "NEUTRAL",
    }
    return mapping.get(direction.lower(), direction.upper())


def _find_indicator(indicators: list[IndicatorSnapshot], name: str) -> IndicatorSnapshot | None:
    for indicator in indicators:
        if indicator.name == name:
            return indicator
    return None


def _format_indicator_value(indicator: IndicatorSnapshot | None, decimals: int) -> str:
    if indicator is None:
        return "No disponible"
    return f"{indicator.value:.{decimals}f}"


def _summary_label(direction: str, confidence: float) -> str:
    if direction == "ALCISTA":
        return (
            "Alcista, importante revisar"
            if confidence >= 75
            else "Alcista, pero aun necesita confirmacion"
        )
    if direction == "BAJISTA":
        return (
            "Bajista, se ve interesante"
            if confidence >= 75
            else "Bajista, pero aun necesita confirmacion"
        )
    if direction == "LATERAL":
        return "En consolidacion, no priorizar"
    return "Sin direccion clara"
