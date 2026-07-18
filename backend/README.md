# Backend — FastAPI

REST API of the platform: authentication, users, datasets, training jobs, deployments. Publishes events to Kafka; never runs heavy work itself (see [docs/architecture.md](../docs/architecture.md)).

## Run

Inside the full stack (recommended):

```bash
docker compose up -d --build   # from the repository root
```

Standalone, for quick iteration:

```bash
cd backend
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Swagger UI: http://localhost:8000/api/docs

## Quality

```bash
ruff check .   # lint
pytest         # tests
```
