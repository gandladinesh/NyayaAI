"""
NyayaAI Backend Application (Phase 1).
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_tables
from app.services.authority_seeder import seed_authorities_database
from app.api.routes import authorities, health, provisions, query

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist and seed baseline authorities and states
    await create_tables()
    await seed_authorities_database()
    yield
    # Shutdown logic if any


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="NyayaAI — AI Legal Assistant for Indian Law with Grounded Legal Evidence",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes with both /api and root prefixes for flexible client consumption
app.include_router(health.router)
app.include_router(health.router, prefix="/api")

app.include_router(authorities.router)
app.include_router(authorities.router, prefix="/api")
app.include_router(provisions.router)
app.include_router(query.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to NyayaAI API",
        "version": settings.app_version,
        "docs_url": "/docs",
    }
