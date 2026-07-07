from backend.application.dto.market_data import AssetMarketStatus
from backend.application.ports.market_data import MarketDataProvider
from backend.infrastructure.config.asset_loader import AssetConfigLoader


class MarketDataService:
    def __init__(
        self, asset_config_loader: AssetConfigLoader, market_data_provider: MarketDataProvider
    ) -> None:
        self._asset_config_loader = asset_config_loader
        self._market_data_provider = market_data_provider

    def get_asset_statuses(self) -> list[AssetMarketStatus]:
        config = self._asset_config_loader.load()
        statuses: list[AssetMarketStatus] = []

        for asset in config.assets:
            if not asset.enabled:
                continue

            timeframe = asset.timeframes[0] if asset.timeframes else None
            provider_symbol = asset.provider_symbols.get(
                self._market_data_provider.provider_name, asset.symbol
            )

            if timeframe is None:
                statuses.append(
                    AssetMarketStatus(
                        symbol=asset.symbol,
                        timeframe=None,
                        provider=self._market_data_provider.provider_name,
                        available=False,
                        candles_loaded=0,
                        last_close=None,
                        message="No timeframe configured for asset.",
                    )
                )
                continue

            try:
                snapshot = self._market_data_provider.get_market_snapshot(provider_symbol, timeframe)
                last_close = snapshot.candles[-1].close if snapshot.candles else None
                statuses.append(
                    AssetMarketStatus(
                        symbol=asset.symbol,
                        timeframe=timeframe.value,
                        provider=snapshot.source,
                        available=True,
                        candles_loaded=len(snapshot.candles),
                        last_close=last_close,
                        message="Market snapshot loaded successfully.",
                    )
                )
            except Exception as exc:
                statuses.append(
                    AssetMarketStatus(
                        symbol=asset.symbol,
                        timeframe=timeframe.value,
                        provider=self._market_data_provider.provider_name,
                        available=False,
                        candles_loaded=0,
                        last_close=None,
                        message=str(exc),
                    )
                )

        return statuses

