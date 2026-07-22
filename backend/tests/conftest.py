from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.events import get_producer
from app.services.storage import get_storage

# In-memory SQLite keeps the test suite fast and dependency-free;
# StaticPool shares the single connection across sessions.
engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class FakeStorage:
    """In-memory stand-in for MinIO so tests need no running object store."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def upload(self, fileobj, key: str, content_type: str | None = None) -> None:
        self.objects[key] = fileobj.read()

    def delete(self, key: str) -> None:
        self.objects.pop(key, None)

    def presigned_download_url(self, key: str, filename: str, expires_in: int = 900) -> str:
        return f"https://storage.test/{key}?expires={expires_in}"


class FakeProducer:
    """Records published events instead of talking to Kafka."""

    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict]] = []

    def publish(self, topic: str, key: str, value: dict) -> None:
        self.events.append((topic, key, value))

    def flush(self, timeout: float = 5.0) -> None:
        pass


@pytest.fixture(autouse=True)
def _fresh_schema() -> Generator[None, None, None]:
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def storage() -> FakeStorage:
    return FakeStorage()


@pytest.fixture
def producer() -> FakeProducer:
    return FakeProducer()


@pytest.fixture
def client(storage: FakeStorage, producer: FakeProducer) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_storage] = lambda: storage
    app.dependency_overrides[get_producer] = lambda: producer
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
