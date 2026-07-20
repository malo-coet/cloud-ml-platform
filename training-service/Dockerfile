FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.29 /uv /uvx /bin/

WORKDIR /app

# Install dependencies first so this layer is cached across code changes
COPY pyproject.toml ./
RUN uv pip install --system --no-cache -r pyproject.toml

COPY trainer ./trainer

CMD ["python", "-m", "trainer.main"]
