from backend.application.services.alert_service import AlertService
from backend.infrastructure.alerts.formatter import TelegramAlertFormatter
from backend.infrastructure.alerts.log_publisher import LogAlertPublisher
from backend.infrastructure.config.asset_loader import AssetConfigLoader
from backend.infrastructure.config.scoring_loader import ScoringConfigLoader
from backend.infrastructure.config.settings import Settings
from backend.infrastructure.indicators.engine import DefaultIndicatorEngine
from backend.infrastructure.market.memory_provider import MemoryMarketDataProvider
from backend.infrastructure.risk.engine import DefaultRiskEngine
from backend.infrastructure.scoring.engine import DefaultScoringEngine
from backend.infrastructure.structure.engine import DefaultStructureEngine


def test_alert_service_builds_previews() -> None:
    scoring_loader = ScoringConfigLoader("config/scoring.yaml")
    service = AlertService(
        Settings(),
        AssetConfigLoader("config/assets.yaml"),
        scoring_loader,
        MemoryMarketDataProvider(),
        DefaultIndicatorEngine(),
        DefaultStructureEngine(),
        DefaultRiskEngine(),
        DefaultScoringEngine(scoring_loader),
        TelegramAlertFormatter(),
        LogAlertPublisher(),
    )

    previews = service.preview_alerts()

    assert len(previews) >= 3
    assert previews[0].symbol == "XAUUSD"
    assert previews[0].channel == "log"

