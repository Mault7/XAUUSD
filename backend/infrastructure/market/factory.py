from backend.application.ports.market_data import MarketDataProvider
from backend.infrastructure.config.settings import Settings
from backend.infrastructure.market.memory_provider import MemoryMarketDataProvider
from backend.infrastructure.market.mt5_provider import MT5MarketDataProvider


def build_market_data_provider(settings: Settings) -> MarketDataProvider:
    provider_name = settings.market_data_provider.lower()

    if provider_name == "mt5":
        return MT5MarketDataProvider(settings)

    return MemoryMarketDataProvider()

