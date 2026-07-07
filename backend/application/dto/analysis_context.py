from dataclasses import dataclass

from backend.domain.entities.alert_message import AlertMessage
from backend.domain.entities.indicator_snapshot import IndicatorSnapshot
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.entities.risk_plan import RiskPlan
from backend.domain.entities.score_breakdown import ScoreBreakdown
from backend.domain.entities.structure_snapshot import StructureSnapshot


@dataclass(frozen=True)
class AssetAnalysisContext:
    asset_symbol: str
    provider_symbol: str
    timeframe: str
    snapshot: MarketSnapshot
    indicators: list[IndicatorSnapshot]
    structure: StructureSnapshot
    risk_plan: RiskPlan
    score: ScoreBreakdown
    alert_message: AlertMessage

