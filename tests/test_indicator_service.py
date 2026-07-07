from backend.infrastructure.config.asset_loader import AssetConfigLoader
from backend.infrastructure.indicators.engine import DefaultIndicatorEngine
from backend.infrastructure.market.memory_provider import MemoryMarketDataProvider
from backend.application.services.indicator_service import IndicatorService


def test_indicator_service_builds_asset_overview() -> None:
    service = IndicatorService(
        AssetConfigLoader("config/assets.yaml"),
        MemoryMarketDataProvider(),
        DefaultIndicatorEngine(),
    )

    overview = service.get_indicator_overview()

    assert len(overview) >= 3
    assert overview[0].symbol == "XAUUSD"
    assert any(indicator.name == "RSI" for indicator in overview[0].indicators)

