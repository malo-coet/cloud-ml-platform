from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness probe used by Docker, Kubernetes and the frontend."""
    return {"status": "ok", "service": settings.app_name, "version": settings.version}
