from backend.domain.value_objects.timeframe import Timeframe

SHORT_TERM_PRIORITY = [
    Timeframe.M15,
    Timeframe.M5,
    Timeframe.H1,
    Timeframe.H4,
    Timeframe.D1,
    Timeframe.W1,
    Timeframe.MN,
]


def select_preferred_timeframe(timeframes: list[Timeframe]) -> str:
    if not timeframes:
        raise ValueError("At least one timeframe is required.")

    available = set(timeframes)
    for timeframe in SHORT_TERM_PRIORITY:
        if timeframe in available:
            return timeframe.value

    return timeframes[0].value
