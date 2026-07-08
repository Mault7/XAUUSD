from backend.application.ports.risk_engine import RiskEngine
from backend.domain.entities.indicator_snapshot import IndicatorSnapshot
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.entities.risk_plan import RiskPlan
from backend.domain.entities.symbol_spec import SymbolSpec
from backend.domain.entities.structure_snapshot import StructureSnapshot
from backend.domain.value_objects.signal_direction import SignalDirection
from backend.infrastructure.config.settings import Settings


class DefaultRiskEngine(RiskEngine):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def build_plan(
        self,
        snapshot: MarketSnapshot,
        symbol_spec: SymbolSpec,
        indicators: list[IndicatorSnapshot],
        structure: StructureSnapshot,
        risk_percent: float,
        account_size: float,
    ) -> RiskPlan:
        last_close = snapshot.candles[-1].close
        direction = _resolve_direction(structure)
        entry = last_close

        if self._settings.risk_mode.lower() == "fixed_loss":
            lot_size = _normalize_volume(self._settings.fixed_lot_size, symbol_spec)
            risk_amount = self._settings.max_loss_usd
            risk_per_unit = _price_distance_for_fixed_loss(symbol_spec, lot_size, risk_amount)
            stop_loss = _stop_from_fixed_loss(entry, direction, risk_per_unit, symbol_spec)
            targets, target_note = _resolve_technical_targets(
                entry=entry,
                direction=direction,
                structure=structure,
                fallback_distance=risk_per_unit,
            )
        else:
            atr = _indicator_value(indicators, "ATR", fallback=max(last_close * 0.002, 0.0001))
            anchor_level = _resolve_anchor_level(structure, direction, last_close)
            stop_buffer = atr * 0.5
            if direction == SignalDirection.BULLISH:
                stop_loss = min(anchor_level, last_close - atr) - stop_buffer
                risk_per_unit = max(entry - stop_loss, 1e-9)
            else:
                stop_loss = max(anchor_level, last_close + atr) + stop_buffer
                risk_per_unit = max(stop_loss - entry, 1e-9)
            risk_amount = account_size * (risk_percent / 100)
            lot_size = round(risk_amount / risk_per_unit, 4)
            targets = _project_r_multiples(entry, direction, risk_per_unit)
            target_note = "Los objetivos se proyectaron en 1R, 2R y 3R."

        take_profit_1, take_profit_2, take_profit_3 = targets
        reward = abs(take_profit_1 - entry)
        risk_reward = round(reward / risk_per_unit, 2)
        explanation = _build_explanation(
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
            risk_amount=risk_amount,
            lot_size=lot_size,
            risk_mode=self._settings.risk_mode,
            target_note=target_note,
        )

        return RiskPlan(
            direction=direction,
            entry=round(entry, 4),
            stop_loss=round(stop_loss, 4),
            take_profit_1=round(take_profit_1, 4),
            take_profit_2=round(take_profit_2, 4),
            take_profit_3=round(take_profit_3, 4),
            risk_percent=risk_percent,
            lot_size=lot_size,
            risk_reward=risk_reward,
            explanation=explanation,
            risk_amount=round(risk_amount, 2),
        )


def _indicator_value(indicators: list[IndicatorSnapshot], name: str, fallback: float) -> float:
    for indicator in indicators:
        if indicator.name == name:
            return indicator.value
    return fallback


def _resolve_direction(structure: StructureSnapshot) -> SignalDirection:
    if structure.trend_bias == SignalDirection.BEARISH:
        return SignalDirection.BEARISH
    return SignalDirection.BULLISH


def _resolve_anchor_level(
    structure: StructureSnapshot, direction: SignalDirection, market_price: float
) -> float:
    if direction == SignalDirection.BULLISH and structure.support_levels:
        return structure.support_levels[-1].price
    if direction == SignalDirection.BEARISH and structure.resistance_levels:
        return structure.resistance_levels[-1].price
    return market_price


def _normalize_volume(volume: float, symbol_spec: SymbolSpec) -> float:
    clamped = min(max(volume, symbol_spec.volume_min), symbol_spec.volume_max)
    steps = round((clamped - symbol_spec.volume_min) / max(symbol_spec.volume_step, 1e-9))
    normalized = symbol_spec.volume_min + steps * symbol_spec.volume_step
    return round(max(normalized, symbol_spec.volume_min), 4)


def _price_distance_for_fixed_loss(
    symbol_spec: SymbolSpec, lot_size: float, risk_amount: float
) -> float:
    monetary_per_price_unit = (symbol_spec.tick_value / symbol_spec.tick_size) * lot_size
    if monetary_per_price_unit <= 0:
        return max(symbol_spec.point, 1e-4)
    raw_distance = risk_amount / monetary_per_price_unit
    min_distance = max(symbol_spec.tick_size, symbol_spec.point, 1e-4)
    ticks = max(round(raw_distance / min_distance), 1)
    return ticks * min_distance


def _stop_from_fixed_loss(
    entry: float,
    direction: SignalDirection,
    risk_per_unit: float,
    symbol_spec: SymbolSpec,
) -> float:
    if direction == SignalDirection.BULLISH:
        return entry - max(risk_per_unit, symbol_spec.tick_size)
    return entry + max(risk_per_unit, symbol_spec.tick_size)


def _resolve_technical_targets(
    *,
    entry: float,
    direction: SignalDirection,
    structure: StructureSnapshot,
    fallback_distance: float,
) -> tuple[tuple[float, float, float], str]:
    candidates: list[float] = []
    if direction == SignalDirection.BULLISH:
        candidates.extend(level.price for level in structure.resistance_levels if level.price > entry)
        candidates.extend(point.price for point in structure.swing_highs if point.price > entry)
        ordered = sorted(set(round(price, 6) for price in candidates))
    else:
        candidates.extend(level.price for level in structure.support_levels if level.price < entry)
        candidates.extend(point.price for point in structure.swing_lows if point.price < entry)
        ordered = sorted(set(round(price, 6) for price in candidates), reverse=True)

    if not ordered:
        return (
            _project_r_multiples(entry, direction, fallback_distance),
            "No habia un objetivo estructural cercano, asi que los objetivos se proyectaron desde la distancia actual del riesgo.",
        )

    targets = ordered[:3]
    while len(targets) < 3:
        if len(targets) == 1:
            extension = abs(targets[0] - entry)
        else:
            extension = abs(targets[-1] - targets[-2])
        extension = max(extension, fallback_distance)
        next_target = targets[-1] + extension if direction == SignalDirection.BULLISH else targets[-1] - extension
        targets.append(round(next_target, 6))

    return (
        (targets[0], targets[1], targets[2]),
        "Los objetivos se anclaron a niveles estructurales cercanos y solo se extendieron cuando faltaban niveles adicionales.",
    )


def _project_r_multiples(
    entry: float,
    direction: SignalDirection,
    risk_per_unit: float,
) -> tuple[float, float, float]:
    if direction == SignalDirection.BULLISH:
        return (
            entry + risk_per_unit,
            entry + risk_per_unit * 2,
            entry + risk_per_unit * 3,
        )
    return (
        entry - risk_per_unit,
        entry - risk_per_unit * 2,
        entry - risk_per_unit * 3,
    )


def _build_explanation(
    *,
    direction: SignalDirection,
    entry: float,
    stop_loss: float,
    risk_amount: float,
    lot_size: float,
    risk_mode: str,
    target_note: str,
) -> str:
    operation = "compra" if direction == SignalDirection.BULLISH else "venta"
    if risk_mode.lower() == "fixed_loss":
        return (
            f"Operacion de {operation} desde {entry:.4f} con stop en {stop_loss:.4f}. "
            f"El modo de perdida fija limita el riesgo estimado a {risk_amount:.2f} USD usando un lote de {lot_size:.2f}. "
            f"{target_note}"
        )
    return (
        f"Operacion de {operation} desde {entry:.4f} con stop en {stop_loss:.4f}. "
        f"El modo porcentual dimensiona la operacion alrededor de {risk_amount:.2f} unidades monetarias de la cuenta. "
        f"{target_note}"
    )
