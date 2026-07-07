from dataclasses import dataclass

from backend.domain.value_objects.signal_direction import SignalDirection


@dataclass(frozen=True)
class SwingPoint:
    kind: str
    price: float
    index: int
    label: str


@dataclass(frozen=True)
class StructureLevel:
    kind: str
    price: float
    explanation: str


@dataclass(frozen=True)
class StructureEvent:
    name: str
    direction: SignalDirection
    strength: float
    explanation: str


@dataclass(frozen=True)
class StructureSnapshot:
    trend_bias: SignalDirection
    swing_highs: list[SwingPoint]
    swing_lows: list[SwingPoint]
    support_levels: list[StructureLevel]
    resistance_levels: list[StructureLevel]
    events: list[StructureEvent]

