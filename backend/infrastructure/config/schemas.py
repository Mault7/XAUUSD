from pydantic import BaseModel, Field

from backend.domain.value_objects.timeframe import Timeframe


class RiskConfig(BaseModel):
    percent: float = Field(gt=0, le=100)


class AssetConfig(BaseModel):
    symbol: str
    enabled: bool = True
    provider_symbols: dict[str, str] = Field(default_factory=dict)
    timeframes: list[Timeframe] = Field(default_factory=list)
    strategies: list[str] = Field(default_factory=list)
    alert_threshold: int = Field(ge=0, le=100)
    risk: RiskConfig


class AssetUniverseConfig(BaseModel):
    assets: list[AssetConfig] = Field(default_factory=list)
