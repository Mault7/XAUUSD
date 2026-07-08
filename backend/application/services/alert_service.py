from datetime import UTC, datetime, timedelta

from backend.application.dto.analysis_context import AssetAnalysisContext
from backend.application.dto.alerts import AlertDispatchResponse, AlertPreviewResponse
from backend.application.services.analysis_pipeline_service import AnalysisPipelineService
from backend.application.services.timeframe_selection import select_configured_timeframe
from backend.application.ports.alert_publisher import AlertPublisher
from backend.domain.entities.indicator_snapshot import IndicatorSnapshot
from backend.domain.entities.score_breakdown import ScoreFactor
from backend.infrastructure.config.asset_loader import AssetConfigLoader
from backend.infrastructure.config.scoring_loader import ScoringConfigLoader
from backend.infrastructure.config.scoring_schemas import AlertingConfig


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
        self._published_alerts: dict[str, datetime] = {}

    def preview_alerts(self) -> list[AlertPreviewResponse]:
        asset_config = self._asset_config_loader.load()
        scoring_config = self._scoring_config_loader.load()
        previews: list[AlertPreviewResponse] = []
        alert_policy = scoring_config.alerting

        for asset in asset_config.assets:
            if not asset.enabled or not asset.timeframes:
                continue

            timeframe = select_configured_timeframe(
                asset.timeframes,
                alert_policy.preferred_timeframe,
            )
            context = self._analysis_pipeline_service.build_asset_context(
                asset_symbol=asset.symbol,
                provider_symbol=asset.provider_symbols.get(
                    self._analysis_pipeline_service.provider_name, asset.symbol
                ),
                timeframe=timeframe,
                risk_percent=asset.risk.percent,
                threshold=float(asset.alert_threshold or scoring_config.defaults.signal_threshold),
            )
            eligible, _ = self._evaluate_alert_eligibility(context, alert_policy)
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
        alert_policy = scoring_config.alerting

        for asset in asset_config.assets:
            if not asset.enabled or not asset.timeframes:
                continue

            timeframe = select_configured_timeframe(
                asset.timeframes,
                alert_policy.preferred_timeframe,
            )
            context = self._analysis_pipeline_service.build_asset_context(
                asset_symbol=asset.symbol,
                provider_symbol=asset.provider_symbols.get(
                    self._analysis_pipeline_service.provider_name, asset.symbol
                ),
                timeframe=timeframe,
                risk_percent=asset.risk.percent,
                threshold=float(asset.alert_threshold or scoring_config.defaults.signal_threshold),
            )
            eligible, reason = self._evaluate_alert_eligibility(context, alert_policy)
            if eligible:
                self._alert_publisher.publish(context.alert_message)
                self._remember_alert(
                    context.asset_symbol,
                    context.timeframe,
                    context.risk_plan.direction.value,
                    context.snapshot.candles[-1].timestamp.isoformat(),
                )
                results.append(
                    AlertDispatchResponse(
                        symbol=asset.symbol,
                        published=True,
                        channel=self._alert_publisher.channel_name,
                        timeframe=context.timeframe,
                        message="Alerta publicada correctamente.",
                    )
                )
            else:
                results.append(
                    AlertDispatchResponse(
                        symbol=asset.symbol,
                        published=False,
                        channel=self._alert_publisher.channel_name,
                        timeframe=context.timeframe,
                        message=reason,
                    )
                )

        return results

    def _evaluate_alert_eligibility(
        self,
        context: AssetAnalysisContext,
        alert_policy: AlertingConfig,
    ) -> tuple[bool, str]:
        if context.structure.trend_bias.value in {"sideways", "neutral"}:
            return False, "Alerta omitida: el mercado sigue en consolidacion o sin direccion clara."

        if context.score.suppressed:
            return False, "Alerta omitida: las reglas de supresion siguen activas."

        if context.score.confidence < context.score.threshold:
            return False, "Alerta omitida: la confianza no alcanzo el umbral configurado."

        trend_alignment = _find_score_factor(context.score.factors, "trend_alignment")
        if (
            trend_alignment is None
            or _factor_strength(trend_alignment) < alert_policy.min_trend_alignment_strength
        ):
            return False, "Alerta omitida: la alineacion direccional todavia no es suficiente."

        structure = _find_score_factor(context.score.factors, "structure")
        if structure is None or _factor_strength(structure) < alert_policy.min_structure_strength:
            return False, "Alerta omitida: la estructura actual no confirma una tendencia interesante."

        if context.risk_plan.risk_reward < alert_policy.min_risk_reward:
            return (
                False,
                f"Alerta omitida: riesgo/beneficio insuficiente ({context.risk_plan.risk_reward:.2f} < {alert_policy.min_risk_reward:.2f}).",
            )

        adx = _find_indicator(context.indicators, "ADX")
        if adx is None or adx.strength < alert_policy.min_adx_strength:
            return False, "Alerta omitida: la fuerza de tendencia segun ADX es demasiado debil."

        atr = _find_indicator(context.indicators, "ATR")
        if atr is None or atr.strength < alert_policy.min_atr_strength:
            return False, "Alerta omitida: la volatilidad actual no es suficiente."

        volume = _find_indicator(context.indicators, "Volume")
        if volume is None or volume.strength < alert_policy.min_volume_strength:
            return False, "Alerta omitida: el volumen no confirma la oportunidad."

        fingerprint = self._build_fingerprint(
            context.asset_symbol,
            context.timeframe,
            context.risk_plan.direction.value,
            context.snapshot.candles[-1].timestamp.isoformat(),
        )
        if self._is_in_cooldown(fingerprint, alert_policy.cooldown_minutes):
            return False, "Alerta omitida: la misma señal sigue en enfriamiento."

        return True, "Alerta apta para publicacion."

    def _build_fingerprint(
        self,
        symbol: str,
        timeframe: str,
        direction: str,
        candle_timestamp: str,
    ) -> str:
        return f"{symbol}|{timeframe}|{direction}|{candle_timestamp}"

    def _is_in_cooldown(self, fingerprint: str, cooldown_minutes: int) -> bool:
        if cooldown_minutes <= 0:
            return False

        published_at = self._published_alerts.get(fingerprint)
        if published_at is None:
            return False

        expires_at = published_at + timedelta(minutes=cooldown_minutes)
        return datetime.now(UTC) < expires_at

    def _remember_alert(
        self,
        symbol: str,
        timeframe: str,
        direction: str,
        candle_timestamp: str,
    ) -> None:
        fingerprint = self._build_fingerprint(symbol, timeframe, direction, candle_timestamp)
        self._published_alerts[fingerprint] = datetime.now(UTC)


def _find_indicator(indicators: list[IndicatorSnapshot], name: str) -> IndicatorSnapshot | None:
    for indicator in indicators:
        if indicator.name == name:
            return indicator
    return None


def _find_score_factor(factors: list[ScoreFactor], name: str) -> ScoreFactor | None:
    for factor in factors:
        if factor.name == name:
            return factor
    return None


def _factor_strength(factor: ScoreFactor) -> float:
    if factor.weight <= 0:
        return 0.0
    return factor.score / factor.weight
