# MLflow tracking server with PostgreSQL and S3 (MinIO) support.
# The official mlflow image ships without DB drivers, hence this custom build.
FROM python:3.12-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
# The full `mlflow server ...` command is provided by docker-compose / Kubernetes.
CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000"]
