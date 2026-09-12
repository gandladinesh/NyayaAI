"""
NyayaAI — Legal Query Service

Combines:
1. RAG retrieval
2. Verified legal provision lookup
3. AI/plain-language explanation
4. Supporting case authorities

The exact legal text remains separate from the AI explanation.
"""

from __future__ import annotations

from app.models.legal_provision import ProvisionCategory
from app.services.ai_explainer import AIExplainer
from app.services.case_authority_service import CaseAuthorityService
from app.services.rag_service import RAGService


class LegalQueryService:
    """Orchestrates legal retrieval, explanation, and authorities."""

    def __init__(self) -> None:
        self.rag = RAGService()
        self.explainer = AIExplainer()
        self.case_authority_service = CaseAuthorityService()

    def answer(
        self,
        question: str,
        category: ProvisionCategory | None = None,
        top_k: int = 3,
    ) -> dict:
        """Retrieve verified legal material and generate an explanation."""

        question = question.strip()

        if not question:
            return {
                "status": "invalid",
                "message": "Please enter a legal question.",
                "primary_result": None,
                "related_results": [],
            }

        results = self.rag.search(
            query=question,
            category=category,
            top_k=top_k,
        )

        if not results:
            return {
                "status": "no_relevant_provision",
                "message": (
                    "I could not find sufficiently relevant verified "
                    "legal material for this question."
                ),
                "primary_result": None,
                "related_results": [],
            }

        def format_result(result: dict) -> dict:
            provision = result["provision"]

            authorities = self.case_authority_service.get_for_provision(
                provision.provision_id
            )

            explanation = self.explainer.explain(
                question=question,
                provision=provision,
            )

            return {
                "provision_id": provision.provision_id,
                "reference_number": provision.reference_number,
                "act": provision.act,
                "exact_text": provision.exact_text,
                "ai_explanation": explanation,
                "official_citation": provision.official_citation,
                "source_name": provision.source_name,
                "source_type": provision.source_type.value,
                "verification_status": provision.verification_status.value,
                "source_url": provision.source_url,
                "distance": result["distance"],
                "case_authorities": [
                    {
                        "case_id": authority.case_id,
                        "case_name": authority.case_name,
                        "citation": authority.citation,
                        "court": authority.court,
                        "judgment_date": authority.judgment_date,
                        "legal_principle": authority.legal_principle,
                        "source_name": authority.source_name,
                        "source_type": authority.source_type,
                        "source_url": authority.source_url,
                        "verification_status": authority.verification_status,
                    }
                    for authority in authorities
                ],
            }

        primary_result = format_result(results[0])

        related_results = [
            format_result(result)
            for result in results[1:]
        ]

        return {
            "status": "success",
            "question": question,
            "primary_result": primary_result,
            "related_results": related_results,
        }