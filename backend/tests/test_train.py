from fastapi.testclient import TestClient

from app.services import mlflow_client
from app.services.events import TOPIC_TRAINING_REQUESTED
from tests.conftest import FakeProducer
from tests.test_auth import ALICE, BOB, register
from tests.test_datasets import auth_header, upload


def queue_job(client: TestClient, headers: dict, dataset_id: str, **overrides) -> dict:
    payload = {"dataset_id": dataset_id, **overrides}
    response = client.post("/api/v1/train", json=payload, headers=headers)
    assert response.status_code == 202, response.text
    return response.json()


def test_train_queues_a_job(client: TestClient) -> None:
    register(client, ALICE)
    headers = auth_header(client, ALICE)
    dataset = upload(client, headers)

    job = queue_job(client, headers, dataset["id"], hyperparameters={"max_iter": 500})

    assert job["status"] == "queued"
    assert job["model_type"] == "logistic_regression"
    assert job["hyperparameters"] == {"max_iter": 500}
    assert job["mlflow_run_id"] is None


def test_train_publishes_training_requested_event(
    client: TestClient, producer: FakeProducer
) -> None:
    register(client, ALICE)
    headers = auth_header(client, ALICE)
    dataset = upload(client, headers)

    job = queue_job(client, headers, dataset["id"])

    assert len(producer.events) == 1
    topic, key, value = producer.events[0]
    assert topic == TOPIC_TRAINING_REQUESTED
    assert key == job["id"]
    assert value["job_id"] == job["id"]
    assert value["dataset_id"] == dataset["id"]


def test_rejected_train_publishes_nothing(client: TestClient, producer: FakeProducer) -> None:
    register(client, ALICE)
    register(client, BOB)
    dataset = upload(client, auth_header(client, ALICE))

    # Bob cannot train on Alice's dataset — no event should be emitted
    client.post(
        "/api/v1/train", json={"dataset_id": dataset["id"]}, headers=auth_header(client, BOB)
    )
    assert producer.events == []


def test_train_rejects_foreign_dataset(client: TestClient) -> None:
    register(client, ALICE)
    register(client, BOB)
    dataset = upload(client, auth_header(client, ALICE))

    response = client.post(
        "/api/v1/train", json={"dataset_id": dataset["id"]}, headers=auth_header(client, BOB)
    )
    assert response.status_code == 404


def test_train_rejects_non_csv_dataset(client: TestClient) -> None:
    register(client, ALICE)
    headers = auth_header(client, ALICE)
    response = client.post(
        "/api/v1/datasets",
        files={"file": ("archive.zip", b"PK\x03\x04fake", "application/zip")},
        headers=headers,
    )
    dataset = response.json()

    train = client.post("/api/v1/train", json={"dataset_id": dataset["id"]}, headers=headers)
    assert train.status_code == 422


def test_jobs_listing_is_per_user(client: TestClient) -> None:
    register(client, ALICE)
    register(client, BOB)
    alice, bob = auth_header(client, ALICE), auth_header(client, BOB)
    dataset = upload(client, alice)
    job = queue_job(client, alice, dataset["id"])

    assert [j["id"] for j in client.get("/api/v1/train", headers=alice).json()] == [job["id"]]
    assert client.get("/api/v1/train", headers=bob).json() == []
    assert client.get(f"/api/v1/train/{job['id']}", headers=bob).status_code == 404


def test_experiments_and_models_proxy_mlflow(client: TestClient, monkeypatch) -> None:
    register(client, ALICE)
    headers = auth_header(client, ALICE)
    runs = [{"run_id": "abc", "experiment": "iris", "metrics": {"accuracy": 0.97}}]
    models = [{"name": "iris-classifier", "latest_versions": [{"version": "1"}]}]
    monkeypatch.setattr(mlflow_client, "list_runs", lambda limit=50: runs)
    monkeypatch.setattr(mlflow_client, "list_registered_models", lambda: models)

    assert client.get("/api/v1/experiments", headers=headers).json() == runs
    assert client.get("/api/v1/models", headers=headers).json() == models


def test_experiments_require_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/experiments").status_code == 401
    assert client.get("/api/v1/models").status_code == 401
