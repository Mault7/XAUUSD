from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    environment: str
    assets: list[str]
    market_provider: str
