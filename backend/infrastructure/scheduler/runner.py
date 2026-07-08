import logging
import time

from backend.api.dependencies.container import get_container

LOGGER = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    container = get_container()
    config = container.scoring_config_loader.load()
    interval = config.alerting.scan_interval_seconds

    LOGGER.info(
        "Iniciando scheduler de alertas automaticas cada %s segundos en canal %s",
        interval,
        container.alert_publisher.channel_name,
    )

    while True:
        try:
            results = container.alert_service.dispatch_alerts()
            published = [result for result in results if result.published]
            LOGGER.info(
                "Ciclo completado. %s alertas publicadas de %s evaluadas.",
                len(published),
                len(results),
            )
        except Exception:  # pragma: no cover - defensive runtime loop
            LOGGER.exception("Fallo durante el ciclo de alertas automaticas")

        time.sleep(interval)


if __name__ == "__main__":
    main()
