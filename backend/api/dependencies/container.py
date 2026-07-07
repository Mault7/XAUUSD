from functools import lru_cache

from backend.application.services.analysis_service import AnalysisService
from backend.application.services.analysis_pipeline_service import AnalysisPipelineService
from backend.application.services.alert_service import AlertService
from backend.application.services.dashboard_service import DashboardService
from backend.application.services.indicator_service import IndicatorService
from backend.application.services.market_data_service import MarketDataService
from backend.application.services.risk_service import RiskService
from backend.application.services.scoring_service import ScoringService
from backend.application.services.structure_service import StructureService
from backend.infrastructure.alerts.factory import build_alert_publisher
from backend.infrastructure.alerts.formatter import TelegramAlertFormatter
from backend.infrastructure.config.asset_loader import AssetConfigLoader
from backend.infrastructure.config.scoring_loader import ScoringConfigLoader
from backend.infrastructure.config.settings import Settings, get_settings
from backend.infrastructure.indicators.engine import DefaultIndicatorEngine
from backend.infrastructure.market.factory import build_market_data_provider
from backend.infrastructure.risk.engine import DefaultRiskEngine
from backend.infrastructure.scoring.engine import DefaultScoringEngine
from backend.infrastructure.structure.engine import DefaultStructureEngine


class AppContainer:
    """Minimal dependency container for the Phase 2 scaffold."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.asset_config_loader = AssetConfigLoader(settings.signal_config_path)
        self.scoring_config_loader = ScoringConfigLoader(settings.scoring_config_path)
        self.market_data_provider = build_market_data_provider(settings)
        self.alert_publisher = build_alert_publisher(settings)
        self.alert_formatter = TelegramAlertFormatter()
        self.indicator_engine = DefaultIndicatorEngine()
        self.structure_engine = DefaultStructureEngine()
        self.risk_engine = DefaultRiskEngine()
        self.scoring_engine = DefaultScoringEngine(self.scoring_config_loader)
        self.analysis_pipeline_service = AnalysisPipelineService(
            settings,
            self.market_data_provider,
            self.indicator_engine,
            self.structure_engine,
            self.risk_engine,
            self.scoring_engine,
            self.alert_formatter,
        )
        self.analysis_service = AnalysisService(self.asset_config_loader, self.market_data_provider)
        self.market_data_service = MarketDataService(
            self.asset_config_loader, self.market_data_provider
        )
        self.indicator_service = IndicatorService(
            self.asset_config_loader,
            self.market_data_provider,
            self.indicator_engine,
        )
        self.structure_service = StructureService(
            self.asset_config_loader,
            self.market_data_provider,
            self.structure_engine,
        )
        self.risk_service = RiskService(
            self.asset_config_loader,
            self.analysis_pipeline_service,
        )
        self.scoring_service = ScoringService(
            self.asset_config_loader,
            self.scoring_config_loader,
            self.analysis_pipeline_service,
        )
        self.alert_service = AlertService(
            self.asset_config_loader,
            self.scoring_config_loader,
            self.analysis_pipeline_service,
            self.alert_publisher,
        )
        self.dashboard_service = DashboardService(
            self.asset_config_loader,
            self.scoring_config_loader,
            self.analysis_pipeline_service,
            self.alert_publisher.channel_name,
        )


@lru_cache(maxsize=1)
def get_container() -> AppContainer:
    return AppContainer(get_settings())
