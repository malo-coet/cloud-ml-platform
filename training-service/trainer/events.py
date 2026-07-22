"""Event schema and (de)serialization — pure, so it is unit-testable without Kafka."""

import json
import uuid
from dataclasses import dataclass

# Topic names — must match the backend producer (see docs/architecture.md)
TOPIC_TRAINING_REQUESTED = "training.requested"
TOPIC_TRAINING_COMPLETED = "training.completed"
TOPIC_TRAINING_DLQ = "training.requested.dlq"


class InvalidEvent(ValueError):
    """Raised for messages that can never be processed (poison → dead-letter)."""


@dataclass(frozen=True)
class TrainingRequested:
    job_id: uuid.UUID


def parse_training_requested(raw: bytes | None) -> TrainingRequested:
    try:
        payload = json.loads(raw) if raw else None
        job_id = uuid.UUID(payload["job_id"])
    except (TypeError, ValueError, KeyError) as exc:
        raise InvalidEvent(f"malformed TrainingRequested event: {exc}") from exc
    return TrainingRequested(job_id=job_id)


def training_completed_payload(
    job_id: str, status: str, run_id: str | None, error: str | None
) -> bytes:
    return json.dumps(
        {"job_id": job_id, "status": status, "mlflow_run_id": run_id, "error": error}
    ).encode()
