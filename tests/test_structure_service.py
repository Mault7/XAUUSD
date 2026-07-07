from backend.application.services.structure_service import StructureService
from backend.infrastructure.config.asset_loader import AssetConfigLoader
from backend.infrastructure.market.memory_provider import MemoryMarketDataProvider
from backend.infrastructure.structure.engine import DefaultStructureEngine


def test_structure_service_builds_asset_overview() -> None:
    service = StructureService(
        AssetConfigLoader("config/assets.yaml"),
        MemoryMarketDataProvider(),
        DefaultStructureEngine(),
    )

    overview = service.get_structure_overview()

    assert len(overview) >= 3
    assert overview[0].symbol == "XAUUSD"
    assert overview[0].events

