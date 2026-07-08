import asyncio
import logging

from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonCommands,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

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
        "Usa los botones para consultar el mercado o, si prefieres, estos comandos:\n"
        "/health - estado del sistema\n"
        "/analyze XAUUSD - analiza un activo\n"
        "/analyze EURUSD H1 - analiza activo y timeframe\n"
        "/scan - escaneo rapido de activos"
    )
    await _reply(update, message, reply_markup=_main_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start_command(update, context)


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    container = get_container()
    message = container.telegram_command_service.health_summary()
    await _reply(update, message, reply_markup=_main_keyboard())


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    container = get_container()
    args = context.args

    if not args:
        await _reply(
            update,
            "Elige un activo para analizar:",
            reply_markup=_analysis_keyboard(),
        )
        return

    symbol = args[0]
    timeframe = args[1].upper() if len(args) > 1 else None
    message = container.telegram_command_service.analyze_asset(symbol, timeframe)
    await _reply(update, message)


async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    container = get_container()
    message = container.telegram_command_service.scan_market()
    await _reply(update, message, reply_markup=_main_keyboard())


async def analyze_text_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message is None or not update.effective_message.text:
        return
    symbol = update.effective_message.text.replace("Analizar ", "", 1).strip()
    await _send_asset_analysis(update, symbol)


async def scan_market_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await scan_command(update, context)


async def health_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await health_command(update, context)


async def analyze_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or query.data is None:
        return

    await query.answer()
    symbol = query.data.split(":", maxsplit=1)[1]
    container = get_container()
    message = container.telegram_command_service.analyze_asset(symbol)
    await query.message.reply_text(message, reply_markup=_main_keyboard())


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(BOT_COMMANDS)
    await application.bot.set_chat_menu_button(menu_button=MenuButtonCommands())


async def _reply(update: Update, message: str, reply_markup: object | None = None) -> None:
    if update.effective_message is not None:
        await update.effective_message.reply_text(message, reply_markup=reply_markup)


async def _send_asset_analysis(update: Update, symbol: str) -> None:
    container = get_container()
    message = container.telegram_command_service.analyze_asset(symbol)
    await _reply(update, message, reply_markup=_main_keyboard())


def _analysis_keyboard() -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    current_row: list[InlineKeyboardButton] = []

    for symbol in _enabled_symbols():
        current_row.append(InlineKeyboardButton(symbol, callback_data=f"analyze:{symbol}"))
        if len(current_row) == 2:
            rows.append(current_row)
            current_row = []

    if current_row:
        rows.append(current_row)

    return InlineKeyboardMarkup(rows or [[InlineKeyboardButton("Sin activos", callback_data="noop")]])


def _main_keyboard() -> ReplyKeyboardMarkup:
    rows: list[list[str]] = []
    current_row: list[str] = []

    for symbol in _enabled_symbols():
        current_row.append(f"Analizar {symbol}")
        if len(current_row) == 2:
            rows.append(current_row)
            current_row = []

    if current_row:
        rows.append(current_row)

    rows.append(["Escanear mercado", "Estado del sistema"])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def _enabled_symbols() -> list[str]:
    container = get_container()
    asset_config = container.asset_config_loader.load()
    return [asset.symbol for asset in asset_config.assets if asset.enabled]


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
    application.add_handler(CallbackQueryHandler(analyze_callback, pattern=r"^analyze:"))
    application.add_handler(MessageHandler(filters.Regex(r"^Analizar .+"), analyze_text_button))
    application.add_handler(
        MessageHandler(filters.Regex("^Escanear mercado$"), scan_market_button)
    )
    application.add_handler(
        MessageHandler(filters.Regex("^Estado del sistema$"), health_button)
    )
    return application


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    application = build_application()
    LOGGER.info("Iniciando bot de Telegram en modo polling")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
