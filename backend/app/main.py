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
    description=(
        "NyayaAI — AI-Powered Legal Assistant for Indian Law\n\n"
        "**Mission:** Provide verified legal information and authority routing for Indian citizens.\n\n"
        "**Core Features:**\n"
        "- **Information Mode** (`POST /api/query`): Search verified legal provisions with AI explanations\n"
        "- **Action Mode** (`GET /api/route`): Find the correct authority and complaint procedures\n"
        "- **Browse Legal Provisions** (`GET /api/provisions`): Browse or search the verified corpus\n"
        "- **Authority Information** (`GET /api/authorities`): Search authorities by state, district, category\n\n"
        "**Architecture:**\n"
        "- **Verified Corpus:** Legal provisions from official government sources (India Code, eCourts)\n"
        "- **RAG System:** Semantic retrieval with AI explanations (Gemini LLM)\n"
        "- **Authority Database:** SQLite (Phase 1) → PostgreSQL ready\n"
        "- **Separation of Concerns:** Exact legal text NEVER AI-generated. Explanations clearly labeled.\n\n"
        "**Documentation:**\n"
        "- Interactive API docs: `/docs`\n"
        "- Alternative docs: `/redoc`\n"
        "- Health check: `/health`\n"
    ),
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


@app.get(
    "/",
    summary="API Root - Welcome and Quick Links",
    tags=["General"],
)
async def root():
    """NyayaAI Backend API Entry Point.
    
    Welcome! This is the NyayaAI backend API.
    
    **Quick Start:**
    1. View interactive documentation: `/docs`
    2. Check service health: `/health`
    3. Query legal information: `POST /api/query`
    4. Route to authority: `GET /api/route`
    
    **Available Endpoints:**
    - **Legal Query** - Search verified provisions with AI explanations
    - **Authority Routing** - Find correct authority and procedures
    - **Provisions** - Browse or search legal corpus
    - **Authorities** - Search and filter authorities by state/district/category
    - **Health** - Service status and version
    """
    return {
        "message": "Welcome to NyayaAI API",
        "version": settings.app_version,
        "docs_url": "/docs",
        "health_url": "/health",
        "quick_start": "Visit /docs for interactive documentation",
    }
