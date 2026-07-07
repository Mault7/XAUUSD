from backend.application.dto.structure import (
    AssetStructureOverviewResponse,
    StructureEventResponse,
    StructureLevelResponse,
    SwingPointResponse,
)
from backend.application.ports.market_data import MarketDataProvider
from backend.application.ports.structure_engine import StructureEngine
from backend.infrastructure.config.asset_loader import AssetConfigLoader


class StructureService:
    def __init__(
        self,
        asset_config_loader: AssetConfigLoader,
        market_data_provider: MarketDataProvider,
        structure_engine: StructureEngine,
    ) -> None:
        self._asset_config_loader = asset_config_loader
        self._market_data_provider = market_data_provider
        self._structure_engine = structure_engine

    def get_structure_overview(self) -> list[AssetStructureOverviewResponse]:
        config = self._asset_config_loader.load()
        overviews: list[AssetStructureOverviewResponse] = []

        for asset in config.assets:
            if not asset.enabled or not asset.timeframes:
                continue

            timeframe = asset.timeframes[0]
            provider_symbol = asset.provider_symbols.get(
                self._market_data_provider.provider_name, asset.symbol
            )
            snapshot = self._market_data_provider.get_market_snapshot(provider_symbol, timeframe)
            structure = self._structure_engine.analyze(snapshot)
            overviews.append(
                AssetStructureOverviewResponse(
                    symbol=asset.symbol,
                    timeframe=timeframe.value,
                    provider=snapshot.source,
                    trend_bias=structure.trend_bias.value,
                    swing_highs=[
                        SwingPointResponse(
                            kind=point.kind,
                            price=point.price,
                            index=point.index,
                            label=point.label,
                        )
                        for point in structure.swing_highs
                    ],
                    swing_lows=[
                        SwingPointResponse(
                            kind=point.kind,
                            price=point.price,
                            index=point.index,
                            label=point.label,
                        )
                        for point in structure.swing_lows
                    ],
                    support_levels=[
                        StructureLevelResponse(
                            kind=level.kind,
                            price=level.price,
                            explanation=level.explanation,
                        )
                        for level in structure.support_levels
                    ],
                    resistance_levels=[
                        StructureLevelResponse(
                            kind=level.kind,
                            price=level.price,
                            explanation=level.explanation,
                        )
                        for level in structure.resistance_levels
                    ],
                    events=[
                        StructureEventResponse(
                            name=event.name,
                            direction=event.direction.value,
                            strength=event.strength,
                            explanation=event.explanation,
                        )
                        for event in structure.events
                    ],
                )
            )

        return overviews

