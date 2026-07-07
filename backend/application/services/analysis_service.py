from backend.application.ports.market_data import MarketDataProvider
from backend.infrastructure.config.asset_loader import AssetConfigLoader


class AnalysisService:
    """Thin application service used to prove the dependency flow."""

    def __init__(
        self, asset_config_loader: AssetConfigLoader, market_data_provider: MarketDataProvider
    ) -> None:
        self._asset_config_loader = asset_config_loader
        self._market_data_provider = market_data_provider

    def get_supported_assets_summary(self) -> list[str]:
        config = self._asset_config_loader.load()
        return [asset.symbol for asset in config.assets if asset.enabled]

    def get_market_provider_name(self) -> str:
        return self._market_data_provider.provider_name
