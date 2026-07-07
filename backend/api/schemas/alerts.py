from pydantic import BaseModel


class AlertPreviewSchema(BaseModel):
    symbol: str
    eligible: bool
    channel: str
    confidence: float
    threshold: float
    suppressed: bool
    message: str


class AlertDispatchSchema(BaseModel):
    symbol: str
    published: bool
    channel: str
    message: str

