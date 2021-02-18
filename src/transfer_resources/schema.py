import typing
from dataclasses import dataclass

import faust
from dataclasses_avroschema import AvroModel
from faust.serializers import codecs
from schema_registry.serializers import FaustSerializer

from src.resources import schema_registry_client

__all__ = ["User", "avro_users_serializer"]


@dataclass
class User(faust.Record, AvroModel, serializer="avro_users"):
    id: str
    name: str
    age: int
    tags: typing.List[str]


avro_users_serializer = FaustSerializer(
    schema_registry_client=schema_registry_client, schema_subject="users", schema=User.avro_schema()
)

codecs.register("avro_users", avro_users_serializer)
