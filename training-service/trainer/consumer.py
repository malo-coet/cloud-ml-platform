"""Kafka consumer: turns TrainingRequested events into training runs.

Replaces the Sprint 4 database polling. Kafka consumer groups guarantee that
each event is handled by a single worker, so replicas scale out safely without
any explicit locking.
"""

import logging
from datetime import UTC, datetime

from confluent_kafka import Consumer, KafkaError, Producer
from confluent_kafka.admin import AdminClient, NewTopic
from sqlalchemy.orm import Session

from trainer.config import settings
from trainer.db import SessionLocal
from trainer.events import (
    TOPIC_TRAINING_COMPLETED,
    TOPIC_TRAINING_DLQ,
    TOPIC_TRAINING_REQUESTED,
    InvalidEvent,
    parse_training_requested,
    training_completed_payload,
)
from trainer.models import TrainingJob
from trainer.runner import process_job

logger = logging.getLogger(__name__)


def ensure_topics() -> None:
    """Create the topics up front (idempotent) so the consumer starts cleanly.

    Single partition / replica suits the single-broker dev cluster; a multi-broker
    production cluster would raise the replication factor.
    """
    admin = AdminClient({"bootstrap.servers": settings.kafka_bootstrap_servers})
    topics = [
        NewTopic(name, num_partitions=1, replication_factor=1)
        for name in (TOPIC_TRAINING_REQUESTED, TOPIC_TRAINING_COMPLETED, TOPIC_TRAINING_DLQ)
    ]
    for name, future in admin.create_topics(topics).items():
        try:
            future.result()
            logger.info("created topic %s", name)
        except Exception:  # noqa: BLE001 — already exists is the common, benign case
            logger.debug("topic %s already exists", name)


def _build_consumer() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": settings.kafka_consumer_group,
            "auto.offset.reset": "earliest",
            # Commit only after a message is fully handled (at-least-once delivery)
            "enable.auto.commit": False,
        }
    )


def _handle_job(session: Session, producer: Producer, job_id) -> None:
    job = session.get(TrainingJob, job_id)
    if job is None:
        raise InvalidEvent(f"job {job_id} does not exist")
    if job.status != "queued":
        # Redelivered event (e.g. after a crash) — already handled, skip it
        logger.info("job %s already '%s' — skipping (idempotent)", job_id, job.status)
        return

    job.status = "running"
    job.started_at = datetime.now(UTC)
    session.commit()
    logger.info("training job %s (model=%s)", job_id, job.model_type)

    process_job(session, job)  # records completed/failed on the job row

    producer.produce(
        TOPIC_TRAINING_COMPLETED,
        key=str(job_id),
        value=training_completed_payload(str(job_id), job.status, job.mlflow_run_id, job.error),
    )
    producer.poll(0)


def _process_message(producer: Producer, raw_key: bytes | None, raw_value: bytes | None) -> None:
    try:
        event = parse_training_requested(raw_value)
    except InvalidEvent as exc:
        logger.error("%s → dead-letter", exc)
        producer.produce(TOPIC_TRAINING_DLQ, key=raw_key, value=raw_value)
        return

    with SessionLocal() as session:
        try:
            _handle_job(session, producer, event.job_id)
        except InvalidEvent as exc:
            logger.error("%s → dead-letter", exc)
            producer.produce(TOPIC_TRAINING_DLQ, key=raw_key, value=raw_value)


def run() -> None:
    ensure_topics()
    consumer = _build_consumer()
    producer = Producer(
        {"bootstrap.servers": settings.kafka_bootstrap_servers, "client.id": "training-service"}
    )
    consumer.subscribe([TOPIC_TRAINING_REQUESTED])
    logger.info(
        "consuming '%s' (group=%s)", TOPIC_TRAINING_REQUESTED, settings.kafka_consumer_group
    )
    try:
        while True:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                # _PARTITION_EOF just means "caught up" — not an error
                if message.error().code() != KafkaError._PARTITION_EOF:
                    logger.error("kafka error: %s", message.error())
                continue
            _process_message(producer, message.key(), message.value())
            consumer.commit(message)
    finally:
        consumer.close()
        producer.flush(5.0)
