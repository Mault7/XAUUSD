from backend.application.dto.risk import RiskPlanResponse
from backend.application.services.analysis_pipeline_service import AnalysisPipelineService
from backend.application.services.timeframe_selection import select_preferred_timeframe
from backend.infrastructure.config.asset_loader import AssetConfigLoader


class RiskService:
    def __init__(
        self,
        asset_config_loader: AssetConfigLoader,
        analysis_pipeline_service: AnalysisPipelineService,
    ) -> None:
        self._asset_config_loader = asset_config_loader
        self._analysis_pipeline_service = analysis_pipeline_service

    def get_risk_overview(self) -> list[RiskPlanResponse]:
        config = self._asset_config_loader.load()
        overviews: list[RiskPlanResponse] = []

        for asset in config.assets:
            if not asset.enabled or not asset.timeframes:
                continue

            context = self._analysis_pipeline_service.build_asset_context(
                asset_symbol=asset.symbol,
                provider_symbol=asset.provider_symbols.get(
                    self._analysis_pipeline_service.provider_name, asset.symbol
                ),
                timeframe=select_preferred_timeframe(asset.timeframes),
                risk_percent=asset.risk.percent,
                threshold=float(asset.alert_threshold),
            )
            overviews.append(
                RiskPlanResponse(
                    symbol=asset.symbol,
                    timeframe=context.timeframe,
                    provider=context.snapshot.source,
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
                )
            )

        return overviews
