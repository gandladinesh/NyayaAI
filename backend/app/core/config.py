"""Application configuration — Gemini, ChromaDB, SQLite (Phase 1)."""

from pathlib import Path
from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ───────────────────────────────────────────────────────────────────
    app_title: str = "NyayaAI Legal Assistant"
    app_version: str = "1.0.0-phase3"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    # ── Database — SQLite for Phase 1, PostgreSQL-ready ───────────────────────
    # To migrate to PostgreSQL: set DATABASE_URL=postgresql+asyncpg://user:pass@host/db
    # No model or service changes required — only this setting.
    database_url: str = "sqlite+aiosqlite:///" + str(Path(__file__).resolve().parents[2] / "nyayaai.db").replace("\\", "/")

    # ── AI Provider: Gemini (Phase 1 decision) ────────────────────────────────
    ai_provider: Literal["gemini", "openai"] = "gemini"
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"
    # OpenAI kept as future option
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"

    # ── Vector Store: ChromaDB (Phase 1 decision) ─────────────────────────────
    # To migrate to pgvector: set vector_store=pgvector and DATABASE_URL to PG
    vector_store: Literal["chromadb", "pgvector"] = "chromadb"
    chroma_persist_directory: str = str(Path(__file__).resolve().parents[2] / "chroma_db").replace("\\", "/")
    chroma_collection_name: str = "nyayaai_provisions"

    # ── IndianKanoon (optional — supplementary source only) ───────────────────
    # If set, enables supplementary lookups. Content is ALWAYS labeled "supplementary".
    # IndianKanoon content NEVER receives source_type="official".
    indian_kanoon_api_key: Optional[str] = None
    indian_kanoon_base_url: str = "https://api.indiankanoon.org"
    indian_kanoon_timeout: int = 30

    # ── Corpus paths ──────────────────────────────────────────────────────────
    seed_corpus_path: str = "data/seed_corpus.json"
    seed_authorities_path: str = "data/seed_authorities.json"

    # ── Cache ─────────────────────────────────────────────────────────────────
    provision_cache_ttl_seconds: int = 86400   # 24 hours
    provision_cache_max_size: int = 1000

    # ── Embeddings ────────────────────────────────────────────────────────────
    embedding_model: str = "models/text-embedding-004"  # Gemini embedding model

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def has_indian_kanoon(self) -> bool:
        return bool(self.indian_kanoon_api_key)

    @property
    def active_ai_api_key(self) -> Optional[str]:
        if self.ai_provider == "gemini":
            return self.gemini_api_key
        return self.openai_api_key


settings = Settings()
