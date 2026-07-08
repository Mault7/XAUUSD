from backend.application.ports.alert_formatter import AlertFormatter
from backend.domain.entities.alert_message import AlertMessage
from backend.domain.entities.indicator_snapshot import IndicatorSnapshot
from backend.domain.entities.risk_plan import RiskPlan
from backend.domain.entities.score_breakdown import ScoreBreakdown
from backend.domain.entities.structure_snapshot import StructureSnapshot


class TelegramAlertFormatter(AlertFormatter):
    def format_message(
        self,
        symbol: str,
        timeframe: str,
        indicators: list[IndicatorSnapshot],
        score_breakdown: ScoreBreakdown,
        risk_plan: RiskPlan,
        structure: StructureSnapshot,
    ) -> AlertMessage:
        direction = _translate_direction(risk_plan.direction.value)
        trend = _translate_direction(structure.trend_bias.value)
        reasons = score_breakdown.reasons[:5] or ["Las condiciones multifactor todavía se están evaluando."]
        rsi = _find_indicator(indicators, "RSI")
        atr = _find_indicator(indicators, "ATR")
        adx = _find_indicator(indicators, "ADX")
        body = "\n".join(
            [
                f"Activo: {symbol}",
                f"Temporalidad: {timeframe}",
                f"Tipo de operacion: {'COMPRA' if direction == 'ALCISTA' else 'VENTA'}",
                f"Direccion: {direction}",
                f"Confianza: {score_breakdown.confidence:.2f}%",
                f"Tendencia: {trend}",
                "",
                "Indicadores clave",
                f"RSI: {_format_indicator_value(rsi, 2)}",
                f"ATR: {_format_indicator_value(atr, 4)}",
                f"ADX: {_format_indicator_value(adx, 2)}",
                "",
                "Razones",
                *[f"- {reason}" for reason in reasons],
                "",
                "Entrada",
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
                "Comentario operativo",
                "Este plan prioriza niveles cercanos cuando la estructura del mercado ofrece objetivos proximos.",
                "",
                "Gestion de riesgo",
                f"Lote: {risk_plan.lot_size:.2f}",
                f"Perdida maxima estimada: {risk_plan.risk_amount:.2f} USD",
                "",
                "Riesgo/Beneficio",
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
