import uuid

from src.config import Config

config = Config(".env")

# Environment
DEBUG = config("DEBUG", cast=bool, default=False)
ENVIRONMENT = config("ENVIRONMENT", default="development")
VERSION = config("VERSION", default=None)
SECRET = config("SECRET", cast=lambda x: uuid.UUID(x, version=4))

# Kafka
KAFKA_URL = config("KAFKA_URL", default=None)
KAFKA_TOPIC = config("KAFKA_TOPIC")
KAFKA_CONSUMER_NAME = config("KAFKA_CONSUMER_NAME", default=f"poc-stream-processor-faust-avro-{ENVIRONMENT!s}")
SCHEMA_REGISTRY_URL = config("SCHEMA_REGISTRY_URL")

# TESTING
TESTING = config("TESTING", cast=bool, default=False)
