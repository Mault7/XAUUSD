import math

from backend.application.ports.indicator_engine import IndicatorEngine
from backend.domain.entities.indicator_snapshot import IndicatorSnapshot
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.value_objects.signal_direction import SignalDirection


class DefaultIndicatorEngine(IndicatorEngine):
    def analyze(self, snapshot: MarketSnapshot) -> list[IndicatorSnapshot]:
        closes = [candle.close for candle in snapshot.candles]
        highs = [candle.high for candle in snapshot.candles]
        lows = [candle.low for candle in snapshot.candles]
        volumes = [candle.volume for candle in snapshot.candles]

        indicators = [
            _ema_snapshot("EMA20", closes, 20),
            _ema_snapshot("EMA50", closes, 50),
            _ema_snapshot("EMA100", closes, 100),
            _ema_snapshot("EMA200", closes, 200),
            _rsi_snapshot(closes, 14),
            _atr_snapshot(highs, lows, closes, 14),
            _macd_snapshot(closes),
            _adx_snapshot(highs, lows, closes, 14),
            _bollinger_snapshot(closes, 20, 2.0),
            _vwap_snapshot(closes, highs, lows, volumes),
            _volume_snapshot(volumes),
        ]
        return indicators


def _ema_snapshot(name: str, closes: list[float], period: int) -> IndicatorSnapshot:
    ema = _ema(closes, period)
    last_close = closes[-1]
    delta = last_close - ema
    strength = _bounded_strength(abs(delta) / ema if ema else 0.0, scale=0.02)
    direction = _direction_from_delta(delta, tolerance=ema * 0.001 if ema else 0.001)
    explanation = f"{name} at {ema:.4f} with price {'above' if delta >= 0 else 'below'} the average."
    return IndicatorSnapshot(name=name, value=ema, direction=direction, strength=strength, explanation=explanation)


def _rsi_snapshot(closes: list[float], period: int) -> IndicatorSnapshot:
    value = _rsi(closes, period)
    if value >= 60:
        direction = SignalDirection.BULLISH
    elif value <= 40:
        direction = SignalDirection.BEARISH
    else:
        direction = SignalDirection.SIDEWAYS
    strength = _bounded_strength(abs(value - 50) / 50, scale=0.6)
    explanation = f"RSI at {value:.2f} indicates {'bullish momentum' if value >= 60 else 'bearish momentum' if value <= 40 else 'balanced momentum'}."
    return IndicatorSnapshot(name="RSI", value=value, direction=direction, strength=strength, explanation=explanation)


def _atr_snapshot(highs: list[float], lows: list[float], closes: list[float], period: int) -> IndicatorSnapshot:
    value = _atr(highs, lows, closes, period)
    baseline = max(sum((high - low) for high, low in zip(highs[-period:], lows[-period:], strict=False)) / period, 1e-9)
    ratio = value / baseline
    if ratio >= 0.9:
        direction = SignalDirection.BULLISH
        explanation_suffix = "healthy volatility for opportunity discovery"
    elif ratio <= 0.5:
        direction = SignalDirection.SIDEWAYS
        explanation_suffix = "compressed volatility that may suppress conviction"
    else:
        direction = SignalDirection.NEUTRAL
        explanation_suffix = "moderate volatility conditions"
    strength = _bounded_strength(ratio, scale=1.0)
    explanation = f"ATR at {value:.4f} shows {explanation_suffix}."
    return IndicatorSnapshot(name="ATR", value=value, direction=direction, strength=strength, explanation=explanation)


def _macd_snapshot(closes: list[float]) -> IndicatorSnapshot:
    macd_line, signal_line, histogram = _macd(closes)
    direction = _direction_from_delta(histogram, tolerance=0.0001)
    strength = _bounded_strength(abs(histogram) / max(abs(macd_line), 1e-9), scale=0.5)
    explanation = f"MACD line {macd_line:.4f}, signal {signal_line:.4f}, histogram {histogram:.4f}."
    return IndicatorSnapshot(name="MACD", value=histogram, direction=direction, strength=strength, explanation=explanation)


def _adx_snapshot(highs: list[float], lows: list[float], closes: list[float], period: int) -> IndicatorSnapshot:
    value, plus_di, minus_di = _adx(highs, lows, closes, period)
    if value >= 25:
        direction = SignalDirection.BULLISH if plus_di >= minus_di else SignalDirection.BEARISH
    else:
        direction = SignalDirection.SIDEWAYS
    strength = _bounded_strength(value / 50, scale=1.0)
    explanation = f"ADX at {value:.2f} with +DI {plus_di:.2f} and -DI {minus_di:.2f}."
    return IndicatorSnapshot(name="ADX", value=value, direction=direction, strength=strength, explanation=explanation)


def _bollinger_snapshot(closes: list[float], period: int, std_dev_multiplier: float) -> IndicatorSnapshot:
    middle, upper, lower = _bollinger_bands(closes, period, std_dev_multiplier)
    last_close = closes[-1]
    band_width = max(upper - lower, 1e-9)
    normalized_position = (last_close - lower) / band_width
    if normalized_position >= 0.65:
        direction = SignalDirection.BULLISH
    elif normalized_position <= 0.35:
        direction = SignalDirection.BEARISH
    else:
        direction = SignalDirection.SIDEWAYS
    strength = _bounded_strength(abs(normalized_position - 0.5) * 2, scale=1.0)
    explanation = f"Bollinger middle {middle:.4f}, upper {upper:.4f}, lower {lower:.4f}."
    return IndicatorSnapshot(name="BollingerBands", value=middle, direction=direction, strength=strength, explanation=explanation)


def _vwap_snapshot(
    closes: list[float], highs: list[float], lows: list[float], volumes: list[float]
) -> IndicatorSnapshot:
    value = _vwap(closes, highs, lows, volumes)
    last_close = closes[-1]
    delta = last_close - value
    direction = _direction_from_delta(delta, tolerance=value * 0.001 if value else 0.001)
    strength = _bounded_strength(abs(delta) / max(value, 1e-9), scale=0.02)
    explanation = f"VWAP at {value:.4f} with price {'above' if delta >= 0 else 'below'} volume-weighted value."
    return IndicatorSnapshot(name="VWAP", value=value, direction=direction, strength=strength, explanation=explanation)


def _volume_snapshot(volumes: list[float]) -> IndicatorSnapshot:
    lookback = min(20, len(volumes))
    average_volume = sum(volumes[-lookback:]) / lookback
    last_volume = volumes[-1]
    ratio = last_volume / max(average_volume, 1e-9)
    if ratio >= 1.1:
        direction = SignalDirection.BULLISH
    elif ratio <= 0.9:
        direction = SignalDirection.BEARISH
    else:
        direction = SignalDirection.NEUTRAL
    strength = _bounded_strength(abs(ratio - 1.0), scale=0.5)
    explanation = f"Volume at {last_volume:.2f} versus {lookback}-bar average {average_volume:.2f}."
    return IndicatorSnapshot(name="Volume", value=last_volume, direction=direction, strength=strength, explanation=explanation)


def _ema(values: list[float], period: int) -> float:
    if len(values) < period:
        raise ValueError(f"Need at least {period} candles for EMA.")
    multiplier = 2 / (period + 1)
    ema_value = sum(values[:period]) / period
    for value in values[period:]:
        ema_value = (value - ema_value) * multiplier + ema_value
    return ema_value


def _rsi(values: list[float], period: int) -> float:
    if len(values) <= period:
        raise ValueError(f"Need more than {period} candles for RSI.")
    gains: list[float] = []
    losses: list[float] = []
    for previous, current in zip(values[:-1], values[1:], strict=False):
        delta = current - previous
        gains.append(max(delta, 0.0))
        losses.append(abs(min(delta, 0.0)))
    average_gain = sum(gains[:period]) / period
    average_loss = sum(losses[:period]) / period
    for gain, loss in zip(gains[period:], losses[period:], strict=False):
        average_gain = ((average_gain * (period - 1)) + gain) / period
        average_loss = ((average_loss * (period - 1)) + loss) / period
    if average_loss == 0:
        return 100.0
    relative_strength = average_gain / average_loss
    return 100 - (100 / (1 + relative_strength))


def _atr(highs: list[float], lows: list[float], closes: list[float], period: int) -> float:
    if len(closes) <= period:
        raise ValueError(f"Need more than {period} candles for ATR.")
    true_ranges: list[float] = []
    for index in range(1, len(closes)):
        high = highs[index]
        low = lows[index]
        previous_close = closes[index - 1]
        true_ranges.append(max(high - low, abs(high - previous_close), abs(low - previous_close)))
    atr_value = sum(true_ranges[:period]) / period
    for true_range in true_ranges[period:]:
        atr_value = ((atr_value * (period - 1)) + true_range) / period
    return atr_value


def _macd(values: list[float]) -> tuple[float, float, float]:
    ema12_series = _ema_series(values, 12)
    ema26_series = _ema_series(values, 26)
    macd_series = [fast - slow for fast, slow in zip(ema12_series[-len(ema26_series):], ema26_series, strict=False)]
    signal_series = _ema_series(macd_series, 9)
    macd_line = macd_series[-1]
    signal_line = signal_series[-1]
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def _adx(highs: list[float], lows: list[float], closes: list[float], period: int) -> tuple[float, float, float]:
    if len(closes) <= period * 2:
        raise ValueError(f"Need more than {period * 2} candles for ADX.")

    true_ranges: list[float] = []
    plus_dm: list[float] = []
    minus_dm: list[float] = []

    for index in range(1, len(closes)):
        up_move = highs[index] - highs[index - 1]
        down_move = lows[index - 1] - lows[index]
        plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0.0)
        minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0.0)
        true_ranges.append(
            max(
                highs[index] - lows[index],
                abs(highs[index] - closes[index - 1]),
                abs(lows[index] - closes[index - 1]),
            )
        )

    atr = sum(true_ranges[:period])
    smoothed_plus_dm = sum(plus_dm[:period])
    smoothed_minus_dm = sum(minus_dm[:period])
    dx_values: list[float] = []

    for index in range(period, len(true_ranges)):
        atr = atr - (atr / period) + true_ranges[index]
        smoothed_plus_dm = smoothed_plus_dm - (smoothed_plus_dm / period) + plus_dm[index]
        smoothed_minus_dm = smoothed_minus_dm - (smoothed_minus_dm / period) + minus_dm[index]

        plus_di = 100 * (smoothed_plus_dm / max(atr, 1e-9))
        minus_di = 100 * (smoothed_minus_dm / max(atr, 1e-9))
        denominator = max(plus_di + minus_di, 1e-9)
        dx_values.append(100 * abs(plus_di - minus_di) / denominator)

    adx = sum(dx_values[:period]) / period
    for dx in dx_values[period:]:
        adx = ((adx * (period - 1)) + dx) / period

    return adx, plus_di, minus_di


def _bollinger_bands(values: list[float], period: int, std_dev_multiplier: float) -> tuple[float, float, float]:
    if len(values) < period:
        raise ValueError(f"Need at least {period} candles for Bollinger Bands.")
    window = values[-period:]
    mean = sum(window) / period
    variance = sum((value - mean) ** 2 for value in window) / period
    std_dev = math.sqrt(variance)
    upper = mean + std_dev_multiplier * std_dev
    lower = mean - std_dev_multiplier * std_dev
    return mean, upper, lower


def _vwap(closes: list[float], highs: list[float], lows: list[float], volumes: list[float]) -> float:
    if not closes or not volumes:
        raise ValueError("Need candles for VWAP.")
    total_price_volume = 0.0
    total_volume = 0.0
    for close, high, low, volume in zip(closes, highs, lows, volumes, strict=False):
        typical_price = (high + low + close) / 3
        total_price_volume += typical_price * volume
        total_volume += volume
    return total_price_volume / max(total_volume, 1e-9)


def _ema_series(values: list[float], period: int) -> list[float]:
    if len(values) < period:
        raise ValueError(f"Need at least {period} candles for EMA series.")
    multiplier = 2 / (period + 1)
    ema_value = sum(values[:period]) / period
    series = [ema_value]
    for value in values[period:]:
        ema_value = (value - ema_value) * multiplier + ema_value
        series.append(ema_value)
    return series


def _direction_from_delta(delta: float, tolerance: float) -> SignalDirection:
    if delta > tolerance:
        return SignalDirection.BULLISH
    if delta < -tolerance:
        return SignalDirection.BEARISH
    return SignalDirection.SIDEWAYS


def _bounded_strength(raw_value: float, scale: float) -> float:
    normalized = raw_value / max(scale, 1e-9)
    return round(min(max(normalized, 0.0), 1.0), 4)

