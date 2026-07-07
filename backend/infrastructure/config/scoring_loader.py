from pathlib import Path

import yaml

from backend.infrastructure.config.scoring_schemas import ScoringConfig


class ScoringConfigLoader:
    def __init__(self, config_path: str) -> None:
        self._config_path = Path(config_path)

    def load(self) -> ScoringConfig:
        with self._config_path.open("r", encoding="utf-8") as handle:
            raw_config = yaml.safe_load(handle) or {}
        return ScoringConfig.model_validate(raw_config)

