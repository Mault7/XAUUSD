import asyncio
import logging

from telegram import BotCommand, MenuButtonCommands, Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes

from backend.api.dependencies.container import get_container
from backend.infrastructure.config.settings import get_settings

LOGGER = logging.getLogger(__name__)

BOT_COMMANDS = [
    BotCommand("start", "Inicia el bot y muestra ayuda"),
    BotCommand("help", "Muestra los comandos disponibles"),
    BotCommand("health", "Estado general del sistema"),
    BotCommand("analyze", "Analiza un activo. Ej: /analyze XAUUSD H1"),
    BotCommand("scan", "Escanea los activos configurados"),
]


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "Trading Signal Assistant listo.\n\n"
        "Comandos disponibles:\n"
        "/health - estado del sistema\n"
        "/analyze XAUUSD - analiza un activo\n"
        "/analyze EURUSD H1 - analiza activo y timeframe\n"
        "/scan - escaneo rápido de activos"
    )
    await _reply(update, message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start_command(update, context)


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    container = get_container()
    message = container.telegram_command_service.health_summary()
    await _reply(update, message)


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    container = get_container()
    args = context.args

    if not args:
        await _reply(update, "Uso: /analyze XAUUSD o /analyze EURUSD H1")
        return

    symbol = args[0]
    timeframe = args[1].upper() if len(args) > 1 else None
    message = container.telegram_command_service.analyze_asset(symbol, timeframe)
    await _reply(update, message)


async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    container = get_container()
    message = container.telegram_command_service.scan_market()
    await _reply(update, message)


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(BOT_COMMANDS)
    await application.bot.set_chat_menu_button(menu_button=MenuButtonCommands())


async def _reply(update: Update, message: str) -> None:
    if update.effective_message is not None:
        await update.effective_message.reply_text(message)


def build_application() -> Application:
    settings = get_settings()
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN no está configurado.")

    application = (
        ApplicationBuilder().token(settings.telegram_bot_token).post_init(post_init).build()
    )
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(CommandHandler("scan", scan_command))
    return application


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    application = build_application()
    LOGGER.info("Starting Telegram bot polling")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
