from backend.application.dto.indicators import AssetIndicatorOverviewResponse, IndicatorValueResponse
from backend.application.ports.indicator_engine import IndicatorEngine
from backend.application.ports.market_data import MarketDataProvider
from backend.infrastructure.config.asset_loader import AssetConfigLoader


class IndicatorService:
    def __init__(
        self,
        asset_config_loader: AssetConfigLoader,
        market_data_provider: MarketDataProvider,
        indicator_engine: IndicatorEngine,
    ) -> None:
        self._asset_config_loader = asset_config_loader
        self._market_data_provider = market_data_provider
        self._indicator_engine = indicator_engine

    def get_indicator_overview(self) -> list[AssetIndicatorOverviewResponse]:
        config = self._asset_config_loader.load()
        overviews: list[AssetIndicatorOverviewResponse] = []

        for asset in config.assets:
            if not asset.enabled or not asset.timeframes:
                continue

            timeframe = asset.timeframes[0]
            provider_symbol = asset.provider_symbols.get(
                self._market_data_provider.provider_name, asset.symbol
            )
            snapshot = self._market_data_provider.get_market_snapshot(provider_symbol, timeframe)
            indicators = self._indicator_engine.analyze(snapshot)
            overviews.append(
                AssetIndicatorOverviewResponse(
                    symbol=asset.symbol,
                    timeframe=timeframe.value,
                    provider=snapshot.source,
                    indicators=[
                        IndicatorValueResponse(
                            name=indicator.name,
                            value=indicator.value,
                            direction=indicator.direction.value,
                            strength=indicator.strength,
                            explanation=indicator.explanation,
                        )
                        for indicator in indicators
                    ],
                )
            )

        return overviews

