"""
NyayaAI - Phase 4: Legal Research Agent
Responsible for retrieving verified legal material using hybrid exact-reference + RAG
and extracting authoritative provisions and court authorities.
"""

from __future__ import annotations

from app.models.legal_provision import ProvisionCategory
from app.services.legal_query_service import LegalQueryService
from app.agents.verification_agent import VerificationAgent, VerificationSummary


class LegalResearchAgent:
    """Retrieves grounded legal evidence from the verified Indian legal corpus."""

    def __init__(
        self,
        query_service: LegalQueryService | None = None,
        verification_agent: VerificationAgent | None = None,
    ) -> None:
        self.query_service = query_service or LegalQueryService()
        self.verification_agent = verification_agent or VerificationAgent()

    def research(
        self,
        question: str,
        category: ProvisionCategory | None = None,
        top_k: int = 3,
        language: str = "en",
    ) -> dict:
        """Executes grounded legal retrieval and returns standardized evidence."""
        # Delegates to LegalQueryService for tested hybrid retrieval & explanation pipeline
        result = self.query_service.answer(
            question=question,
            category=category,
            top_k=top_k,
            language=language,
        )

        return result

