from backend.application.dto.alerts import AlertDispatchResponse, AlertPreviewResponse
from backend.application.services.analysis_pipeline_service import AnalysisPipelineService
from backend.application.ports.alert_publisher import AlertPublisher
from backend.infrastructure.config.asset_loader import AssetConfigLoader
from backend.infrastructure.config.scoring_loader import ScoringConfigLoader


class AlertService:
    def __init__(
        self,
        asset_config_loader: AssetConfigLoader,
        scoring_config_loader: ScoringConfigLoader,
        analysis_pipeline_service: AnalysisPipelineService,
        alert_publisher: AlertPublisher,
    ) -> None:
        self._asset_config_loader = asset_config_loader
        self._scoring_config_loader = scoring_config_loader
        self._analysis_pipeline_service = analysis_pipeline_service
        self._alert_publisher = alert_publisher

    def preview_alerts(self) -> list[AlertPreviewResponse]:
        asset_config = self._asset_config_loader.load()
        scoring_config = self._scoring_config_loader.load()
        previews: list[AlertPreviewResponse] = []

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
            eligible = (not context.score.suppressed) and (
                context.score.confidence >= context.score.threshold
            )
            previews.append(
                AlertPreviewResponse(
                    symbol=asset.symbol,
                    eligible=eligible,
                    channel=self._alert_publisher.channel_name,
                    confidence=context.score.confidence,
                    threshold=context.score.threshold,
                    suppressed=context.score.suppressed,
                    message=context.alert_message.body,
                )
            )

        return previews

    def dispatch_alerts(self) -> list[AlertDispatchResponse]:
        asset_config = self._asset_config_loader.load()
        scoring_config = self._scoring_config_loader.load()
        results: list[AlertDispatchResponse] = []

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
            eligible = (not context.score.suppressed) and (
                context.score.confidence >= context.score.threshold
            )
            if eligible:
                self._alert_publisher.publish(context.alert_message)
                results.append(
                    AlertDispatchResponse(
                        symbol=asset.symbol,
                        published=True,
                        channel=self._alert_publisher.channel_name,
                        message="Alert published successfully.",
                    )
                )
            else:
                results.append(
                    AlertDispatchResponse(
                        symbol=asset.symbol,
                        published=False,
                        channel=self._alert_publisher.channel_name,
                        message="Alert skipped because threshold or suppression rules were not met.",
                    )
                )

        return results
