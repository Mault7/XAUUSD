from backend.application.ports.risk_engine import RiskEngine
from backend.domain.entities.indicator_snapshot import IndicatorSnapshot
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.entities.risk_plan import RiskPlan
from backend.domain.entities.structure_snapshot import StructureSnapshot
from backend.domain.value_objects.signal_direction import SignalDirection


class DefaultRiskEngine(RiskEngine):
    def build_plan(
        self,
        snapshot: MarketSnapshot,
        indicators: list[IndicatorSnapshot],
        structure: StructureSnapshot,
        risk_percent: float,
        account_size: float,
    ) -> RiskPlan:
        last_close = snapshot.candles[-1].close
        atr = _indicator_value(indicators, "ATR", fallback=max(last_close * 0.002, 0.0001))
        direction = _resolve_direction(structure)
        anchor_level = _resolve_anchor_level(structure, direction, last_close)
        stop_buffer = atr * 0.5

        if direction == SignalDirection.BULLISH:
            entry = last_close
            stop_loss = min(anchor_level, last_close - atr) - stop_buffer
            risk_per_unit = max(entry - stop_loss, 1e-9)
            take_profit_1 = entry + risk_per_unit
            take_profit_2 = entry + risk_per_unit * 2
            take_profit_3 = entry + risk_per_unit * 3
        else:
            entry = last_close
            stop_loss = max(anchor_level, last_close + atr) + stop_buffer
            risk_per_unit = max(stop_loss - entry, 1e-9)
            take_profit_1 = entry - risk_per_unit
            take_profit_2 = entry - risk_per_unit * 2
            take_profit_3 = entry - risk_per_unit * 3

        risk_amount = account_size * (risk_percent / 100)
        lot_size = round(risk_amount / risk_per_unit, 4)
        reward = abs(take_profit_2 - entry)
        risk_reward = round(reward / risk_per_unit, 2)
        explanation = (
            f"Entry anchored to latest close {entry:.4f}, stop derived from "
            f"{'support' if direction == SignalDirection.BULLISH else 'resistance'} near {anchor_level:.4f} "
            f"with ATR buffer {atr:.4f}. Targets step out at 1R, 2R, and 3R."
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

