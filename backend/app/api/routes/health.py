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
    - `status`: Current service status (healthy/degraded/offline)
    - `app_title`: NyayaAI application name
    - `app_version`: Current API version
    - `database`: Database type (sqlite for Phase 1, PostgreSQL for production)
    - `phase`: Development phase (Phase 1 Prototype, etc.)
    
    Use this endpoint to verify the service is running before making API calls.
    """
    return {
        "status": "healthy",
        "app_title": settings.app_title,
        "app_version": settings.app_version,
        "database": "sqlite",
        "phase": "Phase 1 Prototype"
    }
