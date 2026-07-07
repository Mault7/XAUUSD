from dataclasses import dataclass


@dataclass(frozen=True)
class AlertMessage:
    channel: str
    subject: str
    body: str
    asset: str
    confidence: float

