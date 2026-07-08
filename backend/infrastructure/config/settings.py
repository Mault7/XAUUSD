from functools import lru_cache

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Trading Signal Assistant", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    debug: bool = Field(default=True, alias="APP_DEBUG")
    host: str = Field(default="0.0.0.0", alias="APP_HOST")
    port: int = Field(default=8000, alias="APP_PORT")
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/trading_signals",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    signal_config_path: str = Field(default="config/assets.yaml", alias="SIGNAL_CONFIG_PATH")
    scoring_config_path: str = Field(default="config/scoring.yaml", alias="SCORING_CONFIG_PATH")
    market_data_provider: str = Field(default="memory", alias="MARKET_DATA_PROVIDER")
    alert_channel: str = Field(default="log", alias="ALERT_CHANNEL")
    account_size: float = Field(default=10000.0, alias="ACCOUNT_SIZE")
    risk_mode: str = Field(default="percent_of_account", alias="RISK_MODE")
    max_loss_usd: float = Field(default=10.0, alias="MAX_LOSS_USD")
    fixed_lot_size: float = Field(default=0.01, alias="FIXED_LOT_SIZE")
    mt5_login: int | None = Field(default=None, alias="MT5_LOGIN")
    mt5_password: str | None = Field(default=None, alias="MT5_PASSWORD")
    mt5_server: str | None = Field(default=None, alias="MT5_SERVER")
    mt5_path: str | None = Field(default=None, alias="MT5_PATH")
    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str | None = Field(default=None, alias="TELEGRAM_CHAT_ID")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator(
        "mt5_login",
        "mt5_password",
        "mt5_server",
        "mt5_path",
        "telegram_bot_token",
        "telegram_chat_id",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value: object) -> object:
        if value == "":
            return None
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
