from backend.application.ports.risk_engine import RiskEngine
from backend.domain.entities.indicator_snapshot import IndicatorSnapshot
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.entities.risk_plan import RiskPlan
from backend.domain.entities.symbol_spec import SymbolSpec
from backend.domain.entities.structure_snapshot import StructureSnapshot
from backend.domain.value_objects.signal_direction import SignalDirection
from backend.domain.value_objects.timeframe import Timeframe
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
        atr = _indicator_value(indicators, "ATR", fallback=max(last_close * 0.002, 0.0001))
        profile = _timeframe_profile(snapshot.timeframe)

        if self._settings.risk_mode.lower() in {"fixed_loss", "fixed_lot"}:
            lot_size = _normalize_volume(self._settings.fixed_lot_size, symbol_spec)
            stop_loss, risk_per_unit, stop_note = _resolve_variable_stop(
                entry=entry,
                direction=direction,
                atr=atr,
                structure=structure,
                timeframe=snapshot.timeframe,
            )
            targets, target_note = _resolve_timeframe_targets(
                entry=entry,
                direction=direction,
                atr=atr,
                structure=structure,
                timeframe=snapshot.timeframe,
                min_distance=risk_per_unit,
            )
            risk_amount = _estimate_risk_amount(symbol_spec, lot_size, risk_per_unit)
        else:
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
            stop_note = (
                f"El stop se calculo con ATR {atr:.4f} y estructura, siguiendo el perfil de {profile.name}."
            )

        take_profit_1, take_profit_2, take_profit_3 = targets
        entry_zone_low, entry_zone_high = _build_entry_zone(
            entry=entry,
            atr=atr,
            risk_per_unit=risk_per_unit,
            timeframe=snapshot.timeframe,
        )
        reward = abs(take_profit_1 - entry)
        risk_reward = round(reward / risk_per_unit, 2)
        explanation = _build_explanation(
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
            risk_amount=risk_amount,
            lot_size=lot_size,
            risk_mode=self._settings.risk_mode,
            stop_note=stop_note,
            target_note=target_note,
        )

        return RiskPlan(
            direction=direction,
            entry=round(entry, 4),
            entry_zone_low=round(entry_zone_low, 4),
            entry_zone_high=round(entry_zone_high, 4),
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


def _resolve_timeframe_targets(
    *,
    entry: float,
    direction: SignalDirection,
    atr: float,
    structure: StructureSnapshot,
    timeframe: Timeframe,
    min_distance: float,
) -> tuple[tuple[float, float, float], str]:
    profile = _timeframe_profile(timeframe)
    candidates = _target_candidates(entry, direction, structure)
    targets: list[float] = []

    for multiplier in profile.target_atr_multipliers:
        cap_distance = max(atr * multiplier, min_distance)
        target = _select_capped_target(
            entry=entry,
            direction=direction,
            candidates=candidates,
            cap_distance=cap_distance,
            previous_target=targets[-1] if targets else None,
        )
        targets.append(round(target, 6))

    return (
        (targets[0], targets[1], targets[2]),
        f"Los objetivos se calcularon con estructura cercana y limites de ATR para {profile.name}, evitando recorridos inflados para este timeframe.",
    )


def _build_entry_zone(
    *,
    entry: float,
    atr: float,
    risk_per_unit: float,
    timeframe: Timeframe,
) -> tuple[float, float]:
    profile = _timeframe_profile(timeframe)
    half_zone = min(
        atr * profile.entry_zone_atr,
        max(risk_per_unit * 0.35, atr * 0.10),
    )
    return entry - half_zone, entry + half_zone


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


def _resolve_variable_stop(
    *,
    entry: float,
    direction: SignalDirection,
    atr: float,
    structure: StructureSnapshot,
    timeframe: Timeframe,
) -> tuple[float, float, str]:
    profile = _timeframe_profile(timeframe)
    buffer = atr * profile.stop_buffer_atr
    min_distance = atr * profile.min_stop_atr
    max_distance = atr * profile.max_stop_atr
    anchor_level = _resolve_anchor_level(structure, direction, entry)

    if direction == SignalDirection.BULLISH:
        structure_stop = anchor_level - buffer
        raw_distance = max(entry - structure_stop, 0.0)
    else:
        structure_stop = anchor_level + buffer
        raw_distance = max(structure_stop - entry, 0.0)

    clamped_distance = min(max(raw_distance, min_distance), max_distance)
    if direction == SignalDirection.BULLISH:
        stop_loss = entry - clamped_distance
    else:
        stop_loss = entry + clamped_distance

    note = (
        f"El stop se ajusto con ATR {atr:.4f}, estructura y limites de {profile.min_stop_atr:.2f} a {profile.max_stop_atr:.2f} ATR para {profile.name}."
    )
    return stop_loss, max(clamped_distance, 1e-9), note


def _estimate_risk_amount(symbol_spec: SymbolSpec, lot_size: float, risk_per_unit: float) -> float:
    monetary_per_price_unit = (symbol_spec.tick_value / max(symbol_spec.tick_size, 1e-9)) * lot_size
    return risk_per_unit * monetary_per_price_unit


def _target_candidates(
    entry: float,
    direction: SignalDirection,
    structure: StructureSnapshot,
) -> list[float]:
    candidates: list[float] = []
    if direction == SignalDirection.BULLISH:
        candidates.extend(level.price for level in structure.resistance_levels if level.price > entry)
        candidates.extend(point.price for point in structure.swing_highs if point.price > entry)
        return sorted(set(round(price, 6) for price in candidates))

    candidates.extend(level.price for level in structure.support_levels if level.price < entry)
    candidates.extend(point.price for point in structure.swing_lows if point.price < entry)
    return sorted(set(round(price, 6) for price in candidates), reverse=True)


def _select_capped_target(
    *,
    entry: float,
    direction: SignalDirection,
    candidates: list[float],
    cap_distance: float,
    previous_target: float | None,
) -> float:
    if direction == SignalDirection.BULLISH:
        fallback = entry + cap_distance
        floor = previous_target if previous_target is not None else entry
        for candidate in candidates:
            if candidate <= floor:
                continue
            if candidate <= fallback:
                return candidate
        return fallback

    fallback = entry - cap_distance
    ceiling = previous_target if previous_target is not None else entry
    for candidate in candidates:
        if candidate >= ceiling:
            continue
        if candidate >= fallback:
            return candidate
    return fallback


class _TimeframeRiskProfile:
    def __init__(
        self,
        *,
        name: str,
        min_stop_atr: float,
        max_stop_atr: float,
        stop_buffer_atr: float,
        entry_zone_atr: float,
        target_atr_multipliers: tuple[float, float, float],
    ) -> None:
        self.name = name
        self.min_stop_atr = min_stop_atr
        self.max_stop_atr = max_stop_atr
        self.stop_buffer_atr = stop_buffer_atr
        self.entry_zone_atr = entry_zone_atr
        self.target_atr_multipliers = target_atr_multipliers


def _timeframe_profile(timeframe: Timeframe) -> _TimeframeRiskProfile:
    profiles = {
        Timeframe.M5: _TimeframeRiskProfile(
            name="M5",
            min_stop_atr=0.60,
            max_stop_atr=1.20,
            stop_buffer_atr=0.12,
            entry_zone_atr=0.18,
            target_atr_multipliers=(0.80, 1.20, 1.80),
        ),
        Timeframe.M15: _TimeframeRiskProfile(
            name="M15",
            min_stop_atr=0.70,
            max_stop_atr=1.50,
            stop_buffer_atr=0.15,
            entry_zone_atr=0.20,
            target_atr_multipliers=(1.00, 1.60, 2.20),
        ),
        Timeframe.H1: _TimeframeRiskProfile(
            name="H1",
            min_stop_atr=0.90,
            max_stop_atr=1.80,
            stop_buffer_atr=0.18,
            entry_zone_atr=0.22,
            target_atr_multipliers=(1.20, 2.00, 2.80),
        ),
        Timeframe.H4: _TimeframeRiskProfile(
            name="H4",
            min_stop_atr=1.00,
            max_stop_atr=2.20,
            stop_buffer_atr=0.22,
            entry_zone_atr=0.25,
            target_atr_multipliers=(1.50, 2.50, 3.50),
        ),
        Timeframe.D1: _TimeframeRiskProfile(
            name="D1",
            min_stop_atr=1.20,
            max_stop_atr=2.60,
            stop_buffer_atr=0.25,
            entry_zone_atr=0.28,
            target_atr_multipliers=(1.80, 3.00, 4.20),
        ),
        Timeframe.W1: _TimeframeRiskProfile(
            name="W1",
            min_stop_atr=1.40,
            max_stop_atr=3.00,
            stop_buffer_atr=0.30,
            entry_zone_atr=0.30,
            target_atr_multipliers=(2.20, 3.60, 5.00),
        ),
        Timeframe.MN: _TimeframeRiskProfile(
            name="MN",
            min_stop_atr=1.60,
            max_stop_atr=3.40,
            stop_buffer_atr=0.35,
            entry_zone_atr=0.35,
            target_atr_multipliers=(2.60, 4.20, 6.00),
        ),
    }
    return profiles[timeframe]


def _build_explanation(
    *,
    direction: SignalDirection,
    entry: float,
    stop_loss: float,
    risk_amount: float,
    lot_size: float,
    risk_mode: str,
    stop_note: str,
    target_note: str,
) -> str:
    operation = "compra" if direction == SignalDirection.BULLISH else "venta"
    if risk_mode.lower() in {"fixed_loss", "fixed_lot"}:
        return (
            f"Operacion de {operation} desde {entry:.4f} con stop en {stop_loss:.4f}. "
            f"El lote fijo de {lot_size:.2f} deja una perdida estimada de {risk_amount:.2f} USD. "
            f"{stop_note} {target_note}"
        )
    return (
        f"Operacion de {operation} desde {entry:.4f} con stop en {stop_loss:.4f}. "
        f"El modo porcentual dimensiona la operacion alrededor de {risk_amount:.2f} unidades monetarias de la cuenta. "
        f"{stop_note} {target_note}"
    )
