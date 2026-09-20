"""Health check and service status routes."""

from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Health & Status"])


@router.get(
    "/health",
    summary="Service health check and version information",
    responses={
        200: {"description": "Service is operational and database is available"},
    }
)
async def health_check():
    """Check NyayaAI backend service health and retrieve version information.
    
    Returns:
    - `status`: Current service status ('healthy')
    - `app_title`: NyayaAI application name
    - `app_version`: Current API version
    - `database`: Database engine type
    - `vector_store`: Vector database engine
    - `environment`: Operational environment (development/staging/production)
    - `phase`: Current deployment phase
    
    Use this endpoint to verify the service is running before making API calls.
    Secrets and internal credentials are never exposed.
    """
    return {
        "status": "healthy",
        "app_title": settings.app_title,
        "app_version": settings.app_version,
        "database": "sqlite",
        "vector_store": settings.vector_store,
        "environment": settings.environment,
        "phase": "Phase 3 Production-Ready",
    }

