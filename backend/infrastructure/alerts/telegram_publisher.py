import asyncio

from backend.application.ports.alert_publisher import AlertPublisher
from backend.domain.entities.alert_message import AlertMessage
from backend.infrastructure.config.settings import Settings

try:
    from telegram import Bot
except ImportError:  # pragma: no cover - optional dependency at runtime
    Bot = None


class TelegramAlertPublisher(AlertPublisher):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def channel_name(self) -> str:
        return "telegram"

    def publish(self, message: AlertMessage) -> None:
        if not self._settings.telegram_bot_token or not self._settings.telegram_chat_id:
            raise RuntimeError("Telegram credentials are not configured.")
        if Bot is None:
            raise RuntimeError("python-telegram-bot is not installed in this environment.")
        bot = Bot(token=self._settings.telegram_bot_token)
        asyncio.run(bot.send_message(chat_id=self._settings.telegram_chat_id, text=message.body))
