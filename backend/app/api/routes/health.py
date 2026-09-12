"""Health check route."""

from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_title": settings.app_title,
        "app_version": settings.app_version,
        "database": "sqlite",
        "phase": "Phase 1 Prototype"
    }
