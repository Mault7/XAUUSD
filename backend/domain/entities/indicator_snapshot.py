from dataclasses import dataclass

from backend.domain.value_objects.signal_direction import SignalDirection


@dataclass(frozen=True)
class IndicatorSnapshot:
    name: str
    value: float
    direction: SignalDirection
    strength: float
    explanation: str

