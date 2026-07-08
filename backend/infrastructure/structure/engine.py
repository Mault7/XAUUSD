from backend.application.ports.structure_engine import StructureEngine
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.entities.structure_snapshot import (
    StructureEvent,
    StructureLevel,
    StructureSnapshot,
    SwingPoint,
)
from backend.domain.value_objects.signal_direction import SignalDirection


class DefaultStructureEngine(StructureEngine):
    def analyze(self, snapshot: MarketSnapshot) -> StructureSnapshot:
        swing_highs = _detect_swings(snapshot, "high")
        swing_lows = _detect_swings(snapshot, "low")
        labeled_highs = _label_swings(swing_highs, is_high=True)
        labeled_lows = _label_swings(swing_lows, is_high=False)
        support_levels = _build_levels(labeled_lows, "support")
        resistance_levels = _build_levels(labeled_highs, "resistance")
        trend_bias = _derive_trend_bias(labeled_highs, labeled_lows)
        events = _derive_structure_events(snapshot, labeled_highs, labeled_lows, trend_bias)

        return StructureSnapshot(
            trend_bias=trend_bias,
            swing_highs=labeled_highs,
            swing_lows=labeled_lows,
            support_levels=support_levels,
            resistance_levels=resistance_levels,
            events=events,
        )


def _detect_swings(snapshot: MarketSnapshot, kind: str, lookback: int = 2) -> list[SwingPoint]:
    points: list[SwingPoint] = []
    candles = snapshot.candles
    for index in range(lookback, len(candles) - lookback):
        center = candles[index]
        previous = candles[index - lookback : index]
        following = candles[index + 1 : index + lookback + 1]

        if kind == "high":
            if all(center.high > candle.high for candle in previous + following):
                points.append(SwingPoint(kind="swing_high", price=center.high, index=index, label="SH"))
        else:
            if all(center.low < candle.low for candle in previous + following):
                points.append(SwingPoint(kind="swing_low", price=center.low, index=index, label="SL"))
    return points[-6:]


def _label_swings(points: list[SwingPoint], *, is_high: bool) -> list[SwingPoint]:
    if not points:
        return []

    labeled: list[SwingPoint] = [points[0]]
    previous = points[0]
    for point in points[1:]:
        if is_high:
            label = "HH" if point.price > previous.price else "LH"
        else:
            label = "HL" if point.price > previous.price else "LL"
        labeled.append(SwingPoint(kind=point.kind, price=point.price, index=point.index, label=label))
        previous = point
    return labeled


def _build_levels(points: list[SwingPoint], level_kind: str) -> list[StructureLevel]:
    levels: list[StructureLevel] = []
    for point in points[-2:]:
        level_label = "Soporte" if level_kind == "support" else "Resistencia"
        explanation = (
            f"{level_label} derivado de {point.label} cerca de la vela indice {point.index}."
        )
        levels.append(StructureLevel(kind=level_kind, price=point.price, explanation=explanation))
    return levels


def _derive_trend_bias(
    swing_highs: list[SwingPoint], swing_lows: list[SwingPoint]
) -> SignalDirection:
    recent_high_labels = {point.label for point in swing_highs[-2:]}
    recent_low_labels = {point.label for point in swing_lows[-2:]}
    if "HH" in recent_high_labels and "HL" in recent_low_labels:
        return SignalDirection.BULLISH
    if "LH" in recent_high_labels and "LL" in recent_low_labels:
        return SignalDirection.BEARISH
    return SignalDirection.SIDEWAYS


def _derive_structure_events(
    snapshot: MarketSnapshot,
    swing_highs: list[SwingPoint],
    swing_lows: list[SwingPoint],
    trend_bias: SignalDirection,
) -> list[StructureEvent]:
    events: list[StructureEvent] = []
    last_close = snapshot.candles[-1].close

    if swing_highs:
        latest_high = swing_highs[-1]
        if last_close > latest_high.price:
            event_name = "BOS" if trend_bias == SignalDirection.BULLISH else "CHOCH"
            direction = SignalDirection.BULLISH
            explanation = (
                f"El precio cerro por encima del ultimo swing high en {latest_high.price:.4f}, senalando {event_name}."
            )
            events.append(
                StructureEvent(
                    name=event_name,
                    direction=direction,
                    strength=_event_strength(last_close, latest_high.price),
                    explanation=explanation,
                )
            )

    if swing_lows:
        latest_low = swing_lows[-1]
        if last_close < latest_low.price:
            event_name = "BOS" if trend_bias == SignalDirection.BEARISH else "CHOCH"
            direction = SignalDirection.BEARISH
            explanation = (
                f"El precio cerro por debajo del ultimo swing low en {latest_low.price:.4f}, senalando {event_name}."
            )
            events.append(
                StructureEvent(
                    name=event_name,
                    direction=direction,
                    strength=_event_strength(latest_low.price, last_close),
                    explanation=explanation,
                )
            )

    if not events:
        explanation = "El precio sigue dentro de los ultimos limites estructurales; no hay BOS ni CHOCH confirmado."
        events.append(
            StructureEvent(
                name="range_bound",
                direction=trend_bias,
                strength=0.3,
                explanation=explanation,
            )
        )

    return events


def _event_strength(reference_a: float, reference_b: float) -> float:
    distance = abs(reference_a - reference_b) / max(abs(reference_b), 1e-9)
    return round(min(max(distance / 0.01, 0.0), 1.0), 4)
