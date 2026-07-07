from backend.application.ports.alert_publisher import AlertPublisher
from backend.infrastructure.alerts.log_publisher import LogAlertPublisher
from backend.infrastructure.alerts.telegram_publisher import TelegramAlertPublisher
from backend.infrastructure.config.settings import Settings


def build_alert_publisher(settings: Settings) -> AlertPublisher:
    if settings.alert_channel.lower() == "telegram":
        return TelegramAlertPublisher(settings)
    return LogAlertPublisher()

