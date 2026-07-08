from backend.application.dto.scoring import AssetScoreOverviewResponse, ScoreFactorResponse
from backend.application.services.analysis_pipeline_service import AnalysisPipelineService
from backend.application.services.timeframe_selection import select_preferred_timeframe
from backend.infrastructure.config.asset_loader import AssetConfigLoader
from backend.infrastructure.config.scoring_loader import ScoringConfigLoader


class ScoringService:
    def __init__(
        self,
        asset_config_loader: AssetConfigLoader,
        scoring_config_loader: ScoringConfigLoader,
        analysis_pipeline_service: AnalysisPipelineService,
    ) -> None:
        self._asset_config_loader = asset_config_loader
        self._scoring_config_loader = scoring_config_loader
        self._analysis_pipeline_service = analysis_pipeline_service

    def get_scoring_overview(self) -> list[AssetScoreOverviewResponse]:
        asset_config = self._asset_config_loader.load()
        scoring_config = self._scoring_config_loader.load()
        overviews: list[AssetScoreOverviewResponse] = []

        for asset in asset_config.assets:
            if not asset.enabled or not asset.timeframes:
                continue

            context = self._analysis_pipeline_service.build_asset_context(
                asset_symbol=asset.symbol,
                provider_symbol=asset.provider_symbols.get(
                    self._analysis_pipeline_service.provider_name, asset.symbol
                ),
                timeframe=select_preferred_timeframe(asset.timeframes),
                risk_percent=asset.risk.percent,
                threshold=float(asset.alert_threshold or scoring_config.defaults.signal_threshold),
            )
            overviews.append(
                AssetScoreOverviewResponse(
                    symbol=asset.symbol,
                    timeframe=context.timeframe,
                    provider=context.snapshot.source,
                    total_score=context.score.total_score,
                    confidence=context.score.confidence,
                    threshold=context.score.threshold,
                    suppressed=context.score.suppressed,
                    reasons=context.score.reasons,
                    factors=[
                        ScoreFactorResponse(
                            name=factor.name,
                            score=factor.score,
                            weight=factor.weight,
                            explanation=factor.explanation,
                        )
                        for factor in context.score.factors
                    ],
                )
            )

        return overviews
