from backend.application.services.analysis_pipeline_service import AnalysisPipelineService
from backend.infrastructure.config.asset_loader import AssetConfigLoader
from backend.infrastructure.config.scoring_loader import ScoringConfigLoader


class TelegramCommandService:
    """Query-oriented application service for Telegram command handlers."""

    def __init__(
        self,
        asset_config_loader: AssetConfigLoader,
        scoring_config_loader: ScoringConfigLoader,
        analysis_pipeline_service: AnalysisPipelineService,
    ) -> None:
        self._asset_config_loader = asset_config_loader
        self._scoring_config_loader = scoring_config_loader
        self._analysis_pipeline_service = analysis_pipeline_service

    def analyze_asset(self, symbol: str, timeframe: str | None = None) -> str:
        asset_config = self._asset_config_loader.load()
        scoring_config = self._scoring_config_loader.load()
        normalized_symbol = symbol.upper()

        for asset in asset_config.assets:
            if asset.symbol.upper() != normalized_symbol:
                continue

            selected_timeframe = timeframe or asset.timeframes[0].value
            threshold = float(asset.alert_threshold or scoring_config.defaults.signal_threshold)
            provider_symbol = asset.provider_symbols.get(
                self._analysis_pipeline_service.provider_name, asset.symbol
            )
            context = self._analysis_pipeline_service.build_asset_context(
                asset_symbol=asset.symbol,
                provider_symbol=provider_symbol,
                timeframe=selected_timeframe,
                risk_percent=asset.risk.percent,
                threshold=threshold,
            )
            return context.alert_message.body

        supported_assets = ", ".join(asset.symbol for asset in asset_config.assets if asset.enabled)
        return f"Activo no soportado: {symbol}. Disponibles: {supported_assets}"

    def scan_market(self) -> str:
        asset_config = self._asset_config_loader.load()
        scoring_config = self._scoring_config_loader.load()
        lines = ["Escaneo de mercado"]

        for asset in asset_config.assets:
            if not asset.enabled or not asset.timeframes:
                continue

            provider_symbol = asset.provider_symbols.get(
                self._analysis_pipeline_service.provider_name, asset.symbol
            )
            context = self._analysis_pipeline_service.build_asset_context(
                asset_symbol=asset.symbol,
                provider_symbol=provider_symbol,
                timeframe=asset.timeframes[0].value,
                risk_percent=asset.risk.percent,
                threshold=float(asset.alert_threshold or scoring_config.defaults.signal_threshold),
            )
            eligible = (not context.score.suppressed) and (
                context.score.confidence >= context.score.threshold
            )
            lines.append(
                f"- {asset.symbol}: {self._translate_direction(context.risk_plan.direction.value)} | "
                f"Confianza {context.score.confidence:.2f} | "
                f"{'ALERTA' if eligible else 'sin alerta'}"
            )

        return "\n".join(lines)

    def health_summary(self) -> str:
        provider = self._analysis_pipeline_service.provider_name
        asset_config = self._asset_config_loader.load()
        enabled_assets = [asset.symbol for asset in asset_config.assets if asset.enabled]
        return (
            "Trading Signal Assistant en linea\n"
            f"Proveedor: {provider}\n"
            f"Activos: {', '.join(enabled_assets)}"
        )

    def _translate_direction(self, direction: str) -> str:
        mapping = {
            "bullish": "ALCISTA",
            "bearish": "BAJISTA",
            "sideways": "LATERAL",
            "neutral": "NEUTRAL",
        }
        return mapping.get(direction.lower(), direction.upper())
