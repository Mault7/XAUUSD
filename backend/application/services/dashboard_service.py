from backend.application.dto.alerts import AlertPreviewResponse
from backend.application.dto.dashboard import (
    AssetDashboardOverviewResponse,
    DashboardAlertResponse,
    DashboardRiskResponse,
    DashboardScoreFactorResponse,
)
from backend.application.dto.indicators import IndicatorValueResponse
from backend.application.dto.structure import (
    StructureEventResponse,
    StructureLevelResponse,
    SwingPointResponse,
)
from backend.application.services.analysis_pipeline_service import AnalysisPipelineService
from backend.infrastructure.config.asset_loader import AssetConfigLoader
from backend.infrastructure.config.scoring_loader import ScoringConfigLoader


class DashboardService:
    def __init__(
        self,
        asset_config_loader: AssetConfigLoader,
        scoring_config_loader: ScoringConfigLoader,
        analysis_pipeline_service: AnalysisPipelineService,
        alert_channel_name: str,
    ) -> None:
        self._asset_config_loader = asset_config_loader
        self._scoring_config_loader = scoring_config_loader
        self._analysis_pipeline_service = analysis_pipeline_service
        self._alert_channel_name = alert_channel_name

    def get_overview(self) -> list[AssetDashboardOverviewResponse]:
        asset_config = self._asset_config_loader.load()
        scoring_config = self._scoring_config_loader.load()
        overview: list[AssetDashboardOverviewResponse] = []

        for asset in asset_config.assets:
            if not asset.enabled or not asset.timeframes:
                continue

            context = self._analysis_pipeline_service.build_asset_context(
                asset_symbol=asset.symbol,
                provider_symbol=asset.provider_symbols.get(
                    self._analysis_pipeline_service.provider_name, asset.symbol
                ),
                timeframe=asset.timeframes[0].value,
                risk_percent=asset.risk.percent,
                threshold=float(asset.alert_threshold or scoring_config.defaults.signal_threshold),
            )
            alert = AlertPreviewResponse(
                symbol=asset.symbol,
                eligible=(not context.score.suppressed)
                and context.score.confidence >= context.score.threshold,
                channel=self._alert_channel_name,
                confidence=context.score.confidence,
                threshold=context.score.threshold,
                suppressed=context.score.suppressed,
                message=context.alert_message.body,
            )
            overview.append(
                AssetDashboardOverviewResponse(
                    symbol=asset.symbol,
                    timeframe=context.timeframe,
                    provider=context.snapshot.source,
                    candles_loaded=len(context.snapshot.candles),
                    last_close=context.snapshot.candles[-1].close if context.snapshot.candles else None,
                    trend_bias=context.structure.trend_bias.value,
                    indicators=[
                        IndicatorValueResponse(
                            name=item.name,
                            value=item.value,
                            direction=item.direction.value,
                            strength=item.strength,
                            explanation=item.explanation,
                        )
                        for item in context.indicators
                    ],
                    swing_highs=[
                        SwingPointResponse(
                            kind=point.kind,
                            price=point.price,
                            index=point.index,
                            label=point.label,
                        )
                        for point in context.structure.swing_highs
                    ],
                    swing_lows=[
                        SwingPointResponse(
                            kind=point.kind,
                            price=point.price,
                            index=point.index,
                            label=point.label,
                        )
                        for point in context.structure.swing_lows
                    ],
                    support_levels=[
                        StructureLevelResponse(
                            kind=level.kind,
                            price=level.price,
                            explanation=level.explanation,
                        )
                        for level in context.structure.support_levels
                    ],
                    resistance_levels=[
                        StructureLevelResponse(
                            kind=level.kind,
                            price=level.price,
                            explanation=level.explanation,
                        )
                        for level in context.structure.resistance_levels
                    ],
                    structure_events=[
                        StructureEventResponse(
                            name=event.name,
                            direction=event.direction.value,
                            strength=event.strength,
                            explanation=event.explanation,
                        )
                        for event in context.structure.events
                    ],
                    risk=DashboardRiskResponse(
                        direction=context.risk_plan.direction.value,
                        entry=context.risk_plan.entry,
                        stop_loss=context.risk_plan.stop_loss,
                        take_profit_1=context.risk_plan.take_profit_1,
                        take_profit_2=context.risk_plan.take_profit_2,
                        take_profit_3=context.risk_plan.take_profit_3,
                        risk_percent=context.risk_plan.risk_percent,
                        lot_size=context.risk_plan.lot_size,
                        risk_reward=context.risk_plan.risk_reward,
                        explanation=context.risk_plan.explanation,
                    ),
                    total_score=context.score.total_score,
                    confidence=context.score.confidence,
                    threshold=context.score.threshold,
                    suppressed=context.score.suppressed,
                    reasons=context.score.reasons,
                    score_factors=[
                        DashboardScoreFactorResponse(
                            name=factor.name,
                            score=factor.score,
                            weight=factor.weight,
                            explanation=factor.explanation,
                        )
                        for factor in context.score.factors
                    ],
                    alert=DashboardAlertResponse(
                        eligible=alert.eligible,
                        channel=alert.channel,
                        confidence=alert.confidence,
                        threshold=alert.threshold,
                        suppressed=alert.suppressed,
                        message=alert.message,
                    ),
                )
            )

        return overview
