from dataclasses import dataclass

from backend.domain.value_objects.signal_direction import SignalDirection


@dataclass(frozen=True)
class RiskPlan:
    direction: SignalDirection
    entry: float
    entry_zone_low: float
    entry_zone_high: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    risk_percent: float
    lot_size: float
    risk_reward: float
    explanation: str
    risk_amount: float = 0.0
