from abc import ABC, abstractmethod

from backend.domain.entities.alert_message import AlertMessage


class AlertPublisher(ABC):
    @property
    @abstractmethod
    def channel_name(self) -> str:
        """Return the publisher channel identifier."""

    @abstractmethod
    def publish(self, message: AlertMessage) -> None:
        """Publish an alert message."""

