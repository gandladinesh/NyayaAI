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



def _relevance_from_distance(distance: float) -> tuple[int, str]:
    """Convert a ChromaDB cosine distance to a citizen-friendly relevance score.

    ChromaDB uses cosine distance: 0.0 = perfect match, 2.0 = completely opposite.
    Exact reference lookups are assigned distance=0.0 by the hybrid retrieval step.

    Returns:
        relevance_score: Integer 0–100 (higher is more relevant).
        confidence_level: 'high' | 'medium' | 'low'

    Thresholds (tuned against the NyayaAI corpus, which uses ChromaDB's default
    all-MiniLM-L6-v2 embedding model):
        high   (score ≥ 75): distance ≤ 0.5
        medium (score ≥ 40): distance ≤ 1.0
        low    (score < 40):  distance > 1.0
    """
    # Clamp distance to [0, 2]
    clamped = max(0.0, min(2.0, distance))
    score = round((1.0 - clamped / 2.0) * 100)

    if score >= 75:
        level = "high"
    elif score >= 40:
        level = "medium"
    else:
        level = "low"

    return score, level


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
        language: str = "en",
    ) -> dict:
        """Retrieve verified legal material and generate an explanation.

        Args:
            question: The legal question from the citizen.
            category: Optional Act/category filter.
            top_k: Maximum number of provisions to retrieve.
            language: ISO 639-1 code for explanation language ('en', 'hi', 'te', 'mr').
                      The exact statutory text is always returned verbatim in English.
        """

        question = question.strip()

        if not question:
            return {
                "status": "invalid",
                "message": "Please enter a legal question.",
                "primary_result": None,
                "related_results": [],
                "language": language,
                "suggestions": [
                    "Try asking about fundamental rights (e.g., 'What is right to life?')",
                    "Ask about criminal law (e.g., 'What is cheating under BNS?')",
                    "Ask about procedure (e.g., 'How is an FIR registered under BNSS?')",
                    "Ask about evidence (e.g., 'Admissibility of electronic evidence under BSA')",
                ],
                "next_steps": [
                    "Enter a specific question describing your situation or legal concern.",
                    "If you know the specific provision, search by reference number (e.g., 'Article 21', 'Section 173').",
                ],
            }

        # Hybrid retrieval: Check if query contains an exact or direct reference
        exact_match = self.rag.legal_service.get_by_reference(
            reference_number=question,
            category=category,
        )

        results = self.rag.search(
            query=question,
            category=category,
            top_k=top_k,
        )

        # If an exact statutory provision was identified, guarantee it appears first
        if exact_match is not None:
            existing_ids = [r["provision"].provision_id for r in results]
            if exact_match.provision_id in existing_ids:
                # Move to front with zero distance
                idx = existing_ids.index(exact_match.provision_id)
                exact_entry = results.pop(idx)
                exact_entry["distance"] = 0.0
                results.insert(0, exact_entry)
            else:
                results.insert(
                    0,
                    {
                        "provision": exact_match,
                        "distance": 0.0,
                    },
                )
            results = results[:top_k]

        if not results:
            return {
                "status": "no_relevant_provision",
                "message": (
                    "I could not find sufficiently relevant verified "
                    "legal material for this question."
                ),
                "primary_result": None,
                "related_results": [],
                "language": language,
                "suggestions": [
                    "Rephrase your question using common legal terms (e.g., 'theft', 'bail', 'FIR', 'equality', 'speedy trial').",
                    "Specify the legal act or category (Constitution, BNS, BNSS, or BSA).",
                    "Search by Article or Section number (e.g., 'Article 21', 'Section 100', 'Section 482').",
                    "Browse all available verified provisions using the /api/provisions endpoint.",
                ],
                "next_steps": [
                    "For free official legal aid, contact your nearest District Legal Services Authority (DLSA) or visit https://nalsa.gov.in.",
                    "For consumer complaints, visit the National Consumer Helpline at https://consumerhelpline.gov.in or call 1915.",
                    "For human rights grievances, approach the State Human Rights Commission (SHRC) or National Human Rights Commission (NHRC).",
                    "Consult a qualified advocate for representation or formal legal advice.",
                ],
            }


        def format_result(result: dict) -> dict:
            provision = result["provision"]
            distance = result["distance"]
            relevance_score, confidence_level = _relevance_from_distance(distance)

            authorities = self.case_authority_service.get_for_provision(
                provision.provision_id
            )

            explanation = self.explainer.explain(
                question=question,
                provision=provision,
                language=language,
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
                "distance": distance,
                "relevance_score": relevance_score,
                "confidence_level": confidence_level,
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
            "language": language,
        }