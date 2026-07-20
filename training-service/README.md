# Training Service

Python worker that executes training jobs queued by the backend (`POST /train`):

1. claims the oldest `queued` job (`SELECT … FOR UPDATE SKIP LOCKED` — safe with multiple replicas),
2. downloads the dataset CSV from MinIO,
3. preprocesses it (drops NA rows, keeps numeric features),
4. trains a classifier (logistic regression or random forest, scikit-learn),
5. logs params, metrics and the model to MLflow and registers it in the **Model Registry** (`{dataset}-classifier`),
6. marks the job `completed` (with the MLflow run id) or `failed` (with the error message).

> Sprint 4 uses database polling as the trigger. Sprint 5 replaces it with a Kafka
> consumer (`TrainingRequested` events); the claim/process/persist core is unchanged.

## Run

Inside the full stack (recommended):

```bash
docker compose up -d --build   # from the repository root
```

## Quality

```bash
cd training-service
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/ruff check .
.venv/bin/pytest
```

The pipeline (`trainer/pipeline.py`) is pure — no database, S3 or MLflow — so tests run without any infrastructure.
