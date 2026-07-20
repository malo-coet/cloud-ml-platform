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

## API overview

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/health` | — | Liveness probe |
| `POST` | `/api/v1/auth/register` | — | Create an account (first user becomes admin) |
| `POST` | `/api/v1/auth/login` | — | OAuth2 password flow, returns a JWT |
| `GET` | `/api/v1/users/me` | JWT | Current user profile |
| `PATCH` | `/api/v1/users/me` | JWT | Update own name / password |
| `GET` | `/api/v1/users` | admin | List users (paginated) |
| `DELETE` | `/api/v1/users/{id}` | admin | Delete a user |
| `POST` | `/api/v1/datasets` | JWT | Upload a dataset file (csv, parquet, zip, png/jpg) |
| `GET` | `/api/v1/datasets` | JWT | List your datasets (each version is an entry) |
| `GET` | `/api/v1/datasets/{id}` | JWT | Dataset metadata |
| `GET` | `/api/v1/datasets/{id}/download` | JWT | Short-lived presigned download URL |
| `DELETE` | `/api/v1/datasets/{id}` | JWT | Delete a dataset version (file + metadata) |
| `POST` | `/api/v1/train` | JWT | Queue a training job (202 — processed asynchronously) |
| `GET` | `/api/v1/train` | JWT | List your training jobs and their status |
| `GET` | `/api/v1/train/{id}` | JWT | Job detail (status, error, MLflow run id) |
| `GET` | `/api/v1/experiments` | JWT | Latest MLflow runs with params and metrics |
| `GET` | `/api/v1/models` | JWT | Models in the MLflow Model Registry |

Dataset files are streamed to MinIO under `datasets/{owner_id}/{name}/v{version}/{filename}`; only metadata (owner, size, format, version) lives in PostgreSQL. Re-uploading under the same name automatically creates a new version.

Passwords are hashed with **Argon2id**; tokens are **HS256 JWTs** (1 h lifetime by default).

## Database migrations

Migrations run automatically when the container starts. Manually:

```bash
alembic upgrade head                          # apply
alembic revision --autogenerate -m "message"  # create from model changes
alembic downgrade -1                          # roll back one step
```

## Quality

```bash
ruff check .   # lint
pytest         # tests
```
