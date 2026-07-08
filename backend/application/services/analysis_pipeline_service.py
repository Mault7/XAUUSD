from backend.application.dto.analysis_context import AssetAnalysisContext
from backend.application.ports.alert_formatter import AlertFormatter
from backend.application.ports.indicator_engine import IndicatorEngine
from backend.application.ports.market_data import MarketDataProvider
from backend.application.ports.risk_engine import RiskEngine
from backend.application.ports.scoring_engine import ScoringEngine
from backend.application.ports.structure_engine import StructureEngine
from backend.infrastructure.config.settings import Settings


class AnalysisPipelineService:
    """Builds a single reusable analysis context for one asset/timeframe."""

    def __init__(
        self,
        settings: Settings,
        market_data_provider: MarketDataProvider,
        indicator_engine: IndicatorEngine,
        structure_engine: StructureEngine,
        risk_engine: RiskEngine,
        scoring_engine: ScoringEngine,
        alert_formatter: AlertFormatter,
    ) -> None:
        self._settings = settings
        self._market_data_provider = market_data_provider
        self._indicator_engine = indicator_engine
        self._structure_engine = structure_engine
        self._risk_engine = risk_engine
        self._scoring_engine = scoring_engine
        self._alert_formatter = alert_formatter

    @property
    def provider_name(self) -> str:
        return self._market_data_provider.provider_name

    def build_asset_context(
        self,
        *,
        asset_symbol: str,
        provider_symbol: str,
        timeframe: str,
        risk_percent: float,
        threshold: float,
    ) -> AssetAnalysisContext:
        from backend.domain.value_objects.timeframe import Timeframe

        snapshot = self._market_data_provider.get_market_snapshot(
            provider_symbol, Timeframe(timeframe)
        )
        symbol_spec = self._market_data_provider.get_symbol_spec(provider_symbol)
        indicators = self._indicator_engine.analyze(snapshot)
        structure = self._structure_engine.analyze(snapshot)
        risk_plan = self._risk_engine.build_plan(
            snapshot=snapshot,
            symbol_spec=symbol_spec,
            indicators=indicators,
            structure=structure,
            risk_percent=risk_percent,
            account_size=self._settings.account_size,
        )
        score = self._scoring_engine.score(
            snapshot=snapshot,
            indicators=indicators,
            structure=structure,
            risk_plan=risk_plan,
            threshold=threshold,
        )
        alert_message = self._alert_formatter.format_message(
            symbol=asset_symbol,
            timeframe=timeframe,
            indicators=indicators,
            score_breakdown=score,
            risk_plan=risk_plan,
            structure=structure,
        )
        return AssetAnalysisContext(
            asset_symbol=asset_symbol,
            provider_symbol=provider_symbol,
            timeframe=timeframe,
            snapshot=snapshot,
            indicators=indicators,
            structure=structure,
            risk_plan=risk_plan,
            score=score,
            alert_message=alert_message,
        )
