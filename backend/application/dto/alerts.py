from pydantic import BaseModel


class AlertPreviewResponse(BaseModel):
    symbol: str
    eligible: bool
    channel: str
    confidence: float
    threshold: float
    suppressed: bool
    message: str


class AlertDispatchResponse(BaseModel):
    symbol: str
    published: bool
    channel: str
    message: str
    timeframe: str | None = None
