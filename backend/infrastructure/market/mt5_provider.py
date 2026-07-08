from datetime import UTC, datetime
from typing import Any

from backend.application.ports.market_data import MarketDataProvider
from backend.domain.entities.candle import Candle
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.entities.symbol_spec import SymbolSpec
from backend.domain.value_objects.timeframe import Timeframe
from backend.infrastructure.config.settings import Settings
from backend.infrastructure.market.exceptions import MarketDataError

try:
    import MetaTrader5 as mt5
except ImportError:  # pragma: no cover - depends on local environment
    mt5 = None


class MT5MarketDataProvider(MarketDataProvider):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def provider_name(self) -> str:
        return "mt5"

    def is_available(self) -> bool:
        return mt5 is not None

    def get_market_snapshot(
        self, symbol: str, timeframe: Timeframe, candles_limit: int = 200
    ) -> MarketSnapshot:
        timeframe_code = _map_timeframe(timeframe)
        with _mt5_session(self._settings):
            rates = mt5.copy_rates_from_pos(symbol, timeframe_code, 0, candles_limit)

        if rates is None:
            raise MarketDataError(f"No MT5 rates returned for {symbol} on {timeframe.value}.")

        candles = [_map_rate_to_candle(rate) for rate in rates]
        return MarketSnapshot(
            symbol=symbol,
            timeframe=timeframe,
            source=self.provider_name,
            fetched_at=datetime.now(UTC),
            candles=candles,
        )

    def get_symbol_spec(self, symbol: str) -> SymbolSpec:
        with _mt5_session(self._settings):
            info = mt5.symbol_info(symbol)

        if info is None:
            raise MarketDataError(f"No MT5 symbol info returned for {symbol}.")

        tick_size = float(info.trade_tick_size or info.point or 0.0)
        tick_value = float(info.trade_tick_value or 0.0)
        if tick_size <= 0:
            raise MarketDataError(f"Invalid tick size returned for {symbol}.")
        if tick_value <= 0:
            raise MarketDataError(f"Invalid tick value returned for {symbol}.")

        return SymbolSpec(
            symbol=symbol,
            point=float(info.point or tick_size),
            tick_size=tick_size,
            tick_value=tick_value,
            contract_size=float(info.trade_contract_size or 0.0),
            volume_min=float(info.volume_min or 0.01),
            volume_step=float(info.volume_step or 0.01),
            volume_max=float(info.volume_max or 100.0),
            profit_currency=str(info.currency_profit or "USD"),
        )


class _mt5_session:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def __enter__(self) -> None:
        if mt5 is None:
            raise MarketDataError("MetaTrader5 package is not installed in this environment.")

        if not mt5.initialize(
            path=self._settings.mt5_path,
            login=self._settings.mt5_login,
            password=self._settings.mt5_password,
            server=self._settings.mt5_server,
        ):
            raise MarketDataError("MetaTrader5 initialize() failed.")
        return None

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        mt5.shutdown()


def _map_timeframe(timeframe: Timeframe) -> int:
    if mt5 is None:
        raise MarketDataError("MetaTrader5 package is not installed in this environment.")

    mapping = {
        Timeframe.MN: mt5.TIMEFRAME_MN1,
        Timeframe.W1: mt5.TIMEFRAME_W1,
        Timeframe.D1: mt5.TIMEFRAME_D1,
        Timeframe.H4: mt5.TIMEFRAME_H4,
        Timeframe.H1: mt5.TIMEFRAME_H1,
        Timeframe.M15: mt5.TIMEFRAME_M15,
        Timeframe.M5: mt5.TIMEFRAME_M5,
    }
    return mapping[timeframe]


def _map_rate_to_candle(rate: Any) -> Candle:
    timestamp = datetime.fromtimestamp(rate["time"], tz=UTC)
    return Candle(
        timestamp=timestamp,
        open=float(rate["open"]),
        high=float(rate["high"]),
        low=float(rate["low"]),
        close=float(rate["close"]),
        volume=float(rate["tick_volume"]),
    )
