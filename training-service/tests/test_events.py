import json
import uuid

import pytest

from trainer.events import (
    InvalidEvent,
    parse_training_requested,
    training_completed_payload,
)


def test_parse_valid_event() -> None:
    job_id = uuid.uuid4()
    raw = json.dumps({"job_id": str(job_id), "model_type": "random_forest"}).encode()

    event = parse_training_requested(raw)

    assert event.job_id == job_id


@pytest.mark.parametrize(
    "raw",
    [
        None,
        b"",
        b"not json",
        b"{}",  # missing job_id
        json.dumps({"job_id": "not-a-uuid"}).encode(),
    ],
)
def test_poison_messages_raise_invalid_event(raw: bytes | None) -> None:
    with pytest.raises(InvalidEvent):
        parse_training_requested(raw)


def test_training_completed_payload_roundtrips() -> None:
    payload = training_completed_payload("job-1", "completed", "run-42", None)
    decoded = json.loads(payload)

    assert decoded == {
        "job_id": "job-1",
        "status": "completed",
        "mlflow_run_id": "run-42",
        "error": None,
    }
