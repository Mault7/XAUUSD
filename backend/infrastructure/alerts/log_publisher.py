from backend.application.ports.alert_publisher import AlertPublisher
from backend.domain.entities.alert_message import AlertMessage


class LogAlertPublisher(AlertPublisher):
    """Development-safe publisher that records messages in memory."""

    def __init__(self) -> None:
        self.messages: list[AlertMessage] = []

    @property
    def channel_name(self) -> str:
        return "log"

    def publish(self, message: AlertMessage) -> None:
        self.messages.append(message)

