from backend.application.ports.scoring_engine import ScoringEngine
from backend.domain.entities.indicator_snapshot import IndicatorSnapshot
from backend.domain.entities.market_snapshot import MarketSnapshot
from backend.domain.entities.risk_plan import RiskPlan
from backend.domain.entities.score_breakdown import ScoreBreakdown, ScoreFactor
from backend.domain.entities.structure_snapshot import StructureSnapshot
from backend.domain.value_objects.signal_direction import SignalDirection
from backend.infrastructure.config.scoring_loader import ScoringConfigLoader


class DefaultScoringEngine(ScoringEngine):
    def __init__(self, scoring_config_loader: ScoringConfigLoader) -> None:
        self._scoring_config_loader = scoring_config_loader

    def score(
        self,
        snapshot: MarketSnapshot,
        indicators: list[IndicatorSnapshot],
        structure: StructureSnapshot,
        risk_plan: RiskPlan,
        threshold: float,
    ) -> ScoreBreakdown:
        config = self._scoring_config_loader.load()
        weights = config.weights

        factors = [
            _factor(
                "trend_alignment",
                weights.trend_alignment,
                _trend_alignment_score(indicators, structure),
                "Measures whether structure and directional indicators agree.",
            ),
            _factor(
                "structure",
                weights.structure,
                _structure_score(structure),
                "Rewards constructive HH/HL or LH/LL sequencing and event quality.",
            ),
            _factor(
                "support_resistance",
                weights.support_resistance,
                _support_resistance_score(snapshot, structure),
                "Scores how cleanly price is positioned relative to nearby structure levels.",
            ),
            _factor("rsi", weights.rsi, _indicator_strength(indicators, "RSI"), "Uses RSI strength."),
            _factor("atr", weights.atr, _indicator_strength(indicators, "ATR"), "Uses ATR health."),
            _factor("macd", weights.macd, _indicator_strength(indicators, "MACD"), "Uses MACD momentum."),
            _factor("adx", weights.adx, _indicator_strength(indicators, "ADX"), "Uses ADX trend quality."),
            _factor("volume", weights.volume, _indicator_strength(indicators, "Volume"), "Uses volume expansion."),
            _factor(
                "smart_money",
                weights.smart_money,
                _smart_money_placeholder(structure),
                "Placeholder confluence score until smart-money detection is implemented.",
            ),
            _factor(
                "news_filter",
                weights.news_filter,
                1.0,
                "Neutral news score until economic calendar suppression is implemented.",
            ),
        ]

        total_score = round(sum(factor.score for factor in factors), 2)
        confidence = round(min(max(total_score, 0.0), 100.0), 2)
        suppressed = confidence < max(threshold, config.defaults.suppression_floor) or risk_plan.risk_reward < 1.5
        reasons = [factor.explanation for factor in factors if factor.score >= factor.weight * 0.6]
        if risk_plan.risk_reward < 1.5:
            reasons.append("Risk/reward is below the current acceptance floor.")

        return ScoreBreakdown(
            total_score=total_score,
            confidence=confidence,
            threshold=threshold,
            suppressed=suppressed,
            reasons=reasons,
            factors=factors,
        )


def _factor(name: str, weight: float, normalized_score: float, explanation: str) -> ScoreFactor:
    realized = round(weight * min(max(normalized_score, 0.0), 1.0), 2)
    return ScoreFactor(name=name, score=realized, weight=weight, explanation=explanation)


def _indicator_strength(indicators: list[IndicatorSnapshot], name: str) -> float:
    for indicator in indicators:
        if indicator.name == name:
            return indicator.strength
    return 0.0


def _trend_alignment_score(
    indicators: list[IndicatorSnapshot], structure: StructureSnapshot
) -> float:
    bullish_votes = 0
    bearish_votes = 0
    for indicator in indicators:
        if indicator.direction == SignalDirection.BULLISH:
            bullish_votes += 1
        elif indicator.direction == SignalDirection.BEARISH:
            bearish_votes += 1

    if structure.trend_bias == SignalDirection.BULLISH:
        bullish_votes += 2
    elif structure.trend_bias == SignalDirection.BEARISH:
        bearish_votes += 2

    total_votes = max(bullish_votes + bearish_votes, 1)
    dominant_votes = max(bullish_votes, bearish_votes)
    return dominant_votes / total_votes


def _structure_score(structure: StructureSnapshot) -> float:
    event_strength = max((event.strength for event in structure.events), default=0.3)
    if structure.trend_bias == SignalDirection.SIDEWAYS:
        return min(0.45 + event_strength * 0.2, 0.6)
    return min(0.6 + event_strength * 0.4, 1.0)


def _support_resistance_score(snapshot: MarketSnapshot, structure: StructureSnapshot) -> float:
    last_close = snapshot.candles[-1].close
    if structure.trend_bias == SignalDirection.BULLISH and structure.support_levels:
        distance = abs(last_close - structure.support_levels[-1].price) / max(last_close, 1e-9)
    elif structure.trend_bias == SignalDirection.BEARISH and structure.resistance_levels:
        distance = abs(last_close - structure.resistance_levels[-1].price) / max(last_close, 1e-9)
    else:
        return 0.4
    return max(0.0, min(1 - (distance / 0.02), 1.0))


def _smart_money_placeholder(structure: StructureSnapshot) -> float:
    if any(event.name == "BOS" for event in structure.events):
        return 0.7
    if structure.trend_bias != SignalDirection.SIDEWAYS:
        return 0.5
    return 0.3

