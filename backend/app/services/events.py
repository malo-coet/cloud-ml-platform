"""Kafka event producer.

The API publishes facts (e.g. TrainingRequested) and returns immediately;
workers react to them. This keeps the request path fast and decoupled from
the workers' availability.
"""

import json
import logging
from functools import lru_cache
from typing import Annotated

from confluent_kafka import Producer as KafkaProducer
from fastapi import Depends

from app.core.config import settings

logger = logging.getLogger(__name__)

# Topic names — see docs/architecture.md for the event catalogue
TOPIC_TRAINING_REQUESTED = "training.requested"


class EventProducer:
    """Thin JSON wrapper around a confluent-kafka producer."""

    def __init__(self, bootstrap_servers: str) -> None:
        # librdkafka connects in the background and buffers locally, so this
        # never blocks even if the broker is not reachable yet.
        self._producer = KafkaProducer(
            {"bootstrap.servers": bootstrap_servers, "client.id": "backend"}
        )

    def publish(self, topic: str, key: str, value: dict) -> None:
        self._producer.produce(topic, key=key, value=json.dumps(value).encode())
        self._producer.poll(0)  # serve delivery callbacks without blocking

    def flush(self, timeout: float = 5.0) -> None:
        self._producer.flush(timeout)


@lru_cache
def get_producer() -> EventProducer:
    return EventProducer(settings.kafka_bootstrap_servers)


def producer_was_created() -> bool:
    """True once get_producer() has built a producer — used to flush on shutdown."""
    return get_producer.cache_info().currsize > 0


Producer = Annotated[EventProducer, Depends(get_producer)]
