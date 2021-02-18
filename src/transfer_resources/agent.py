import logging
import typing

import faust

from src import settings
from src.resources import faust_app
from src.transfer_resources import schema

logger = logging.getLogger(__name__)

__all__ = ["topic", "processor_function"]


topic = faust_app.topic(settings.KAFKA_TOPIC, value_type=schema.User)


@faust_app.agent(topic)
async def processor_function(messages: faust.Stream) -> typing.AsyncGenerator[schema.User, None]:
    """
    Faust agent that does cool stuff with incoming messages.

    :param messages: Kafka messages.
    """

    # Example of messages filtering by some criteria
    messages = messages.filter(lambda msg: msg.age >= 18)

    async for message in messages:
        # Do some fancy stuff with the message
        yield message
