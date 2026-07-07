from backend.application.services.scoring_service import ScoringService
from backend.infrastructure.config.asset_loader import AssetConfigLoader
from backend.infrastructure.config.scoring_loader import ScoringConfigLoader
from backend.infrastructure.config.settings import Settings
from backend.infrastructure.indicators.engine import DefaultIndicatorEngine
from backend.infrastructure.market.memory_provider import MemoryMarketDataProvider
from backend.infrastructure.risk.engine import DefaultRiskEngine
from backend.infrastructure.scoring.engine import DefaultScoringEngine
from backend.infrastructure.structure.engine import DefaultStructureEngine


def test_scoring_service_builds_asset_overview() -> None:
    loader = ScoringConfigLoader("config/scoring.yaml")
    service = ScoringService(
        Settings(),
        AssetConfigLoader("config/assets.yaml"),
        loader,
        MemoryMarketDataProvider(),
        DefaultIndicatorEngine(),
        DefaultStructureEngine(),
        DefaultRiskEngine(),
        DefaultScoringEngine(loader),
    )

    overview = service.get_scoring_overview()

    assert len(overview) >= 3
    assert overview[0].symbol == "XAUUSD"
    assert overview[0].factors

