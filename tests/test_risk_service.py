from backend.application.services.risk_service import RiskService
from backend.infrastructure.config.asset_loader import AssetConfigLoader
from backend.infrastructure.config.settings import Settings
from backend.infrastructure.indicators.engine import DefaultIndicatorEngine
from backend.infrastructure.market.memory_provider import MemoryMarketDataProvider
from backend.infrastructure.risk.engine import DefaultRiskEngine
from backend.infrastructure.structure.engine import DefaultStructureEngine


def test_risk_service_builds_asset_overview() -> None:
    service = RiskService(
        Settings(),
        AssetConfigLoader("config/assets.yaml"),
        MemoryMarketDataProvider(),
        DefaultIndicatorEngine(),
        DefaultStructureEngine(),
        DefaultRiskEngine(),
    )

    overview = service.get_risk_overview()

    assert len(overview) >= 3
    assert overview[0].symbol == "XAUUSD"
    assert overview[0].entry > 0

