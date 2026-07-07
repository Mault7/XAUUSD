from pydantic import BaseModel


class RiskPlanResponse(BaseModel):
    symbol: str
    timeframe: str
    provider: str
    direction: str
    entry: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    risk_percent: float
    lot_size: float
    risk_reward: float
    explanation: str

