import faust
from schema_registry.client import SchemaRegistryClient

from src import settings

__all__ = ["faust_app", "schema_registry_client"]


faust_app = faust.App(
    id=settings.KAFKA_CONSUMER_NAME,
    broker=settings.KAFKA_URL,
    autodiscover=["src.transfer_resources.agent", "src.core.pages"],
    origin="src",
    _broker_session_timeout=10,
    logging_config={
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "default": {"level": "DEBUG", "formatter": "standard", "class": "logging.StreamHandler"},
            "cron_file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "/srv/app/logs/app.log",
                "formatter": "standard",
                "backupCount": 30,
            },
        },
        "loggers": {"src": {"handlers": ["default", "cron_file"], "level": "INFO", "propagate": False}},
    },
)

schema_registry_client = SchemaRegistryClient(url=settings.SCHEMA_REGISTRY_URL)
