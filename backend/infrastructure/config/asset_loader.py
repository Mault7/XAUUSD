from pathlib import Path

import yaml

from backend.infrastructure.config.schemas import AssetUniverseConfig


class AssetConfigLoader:
    def __init__(self, config_path: str) -> None:
        self._config_path = Path(config_path)

    def load(self) -> AssetUniverseConfig:
        with self._config_path.open("r", encoding="utf-8") as handle:
            raw_config = yaml.safe_load(handle) or {}
        return AssetUniverseConfig.model_validate(raw_config)

