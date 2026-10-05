"""
NyayaAI - Phase 4: Controlled Agent Orchestrator
Coordinates query classification, workflow selection, legal research,
evidence verification, and safe citizen-oriented response generation.
"""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field

from app.models.legal_provision import ProvisionCategory
from app.agents.query_classifier import QueryClassifier, ClassificationResult, LegalDomain, QueryIntent
from app.agents.legal_research_agent import LegalResearchAgent
from app.agents.verification_agent import VerificationAgent, VerificationSummary
from app.agents.action_agent import ActionAgent


class AgentResult(BaseModel):
    """Structured internal result representing the state of the agentic pipeline."""
    intent: QueryIntent = Field(description="Detected user intent")
    domain: LegalDomain = Field(description="Detected legal domain")
    workflow: str = Field(description="Executed agentic workflow")
    verification: VerificationSummary = Field(description="Evidence verification summary")
    answer_source: str = Field(description="Source of the answer: verified_corpus | curated_fallback | action_router")
    confidence: float = Field(ge=0.0, le=1.0, description="Overall pipeline confidence")
    needs_more_information: bool = Field(default=False, description="Flag indicating if the query is too ambiguous")
    raw_response: dict[str, Any] = Field(description="Backward-compatible response payload")


class AgentOrchestrator:
    """Master orchestrator for the NyayaAI Agentic System."""

    def __init__(
        self,
        classifier: QueryClassifier | None = None,
        research_agent: LegalResearchAgent | None = None,
        verification_agent: VerificationAgent | None = None,
        action_agent: ActionAgent | None = None,
    ) -> None:
        self.classifier = classifier or QueryClassifier()
        self.research_agent = research_agent or LegalResearchAgent()
        self.verification_agent = verification_agent or VerificationAgent()
        self.action_agent = action_agent or ActionAgent()

    def handle_query(
        self,
        question: str,
        category: ProvisionCategory | None = None,
        top_k: int = 3,
        language: str = "en",
    ) -> dict[str, Any]:
        """Execute the agentic workflow and return a backward-compatible response dict."""
        agent_result = self.execute_agent_pipeline(
            question=question,
            category=category,
            top_k=top_k,
            language=language,
        )
        return agent_result.raw_response

    def execute_agent_pipeline(
        self,
        question: str,
        category: ProvisionCategory | None = None,
        top_k: int = 3,
        language: str = "en",
    ) -> AgentResult:
        """Executes the full controlled agent pipeline and produces an AgentResult."""
        # 1. Step 1: Query Classification (Zero-cost deterministic)
        classification: ClassificationResult = self.classifier.classify(question)

        # 2. Step 2: Determine category override if user did not explicitly provide one
        effective_category = category
        if effective_category is None and classification.suggested_category_filter:
            try:
                effective_category = ProvisionCategory(classification.suggested_category_filter)
            except Exception:
                effective_category = None

        # 3. Step 3: Legal Research & Evidence Retrieval
        research_output = self.research_agent.research(
            question=question,
            category=effective_category,
            top_k=top_k,
            language=language,
        )

        # If filtered search yielded no relevant provisions, retry without filter to prevent false negatives
        if research_output.get("status") == "no_relevant_provision" and effective_category is not None and category is None:
            research_output = self.research_agent.research(
                question=question,
                category=None,
                top_k=top_k,
                language=language,
            )

        # 4. Step 4: Verification of Evidence
        relevance_score = None
        if research_output.get("primary_result"):
            relevance_score = research_output["primary_result"].get("relevance_score")

        results_to_verify = []
        if research_output.get("primary_result"):
            results_to_verify.append(research_output["primary_result"])
        if research_output.get("related_results"):
            results_to_verify.extend(research_output["related_results"])

        verification: VerificationSummary = self.verification_agent.verify_evidence(
            retrieved_results=results_to_verify,
            relevance_score=relevance_score,
        )

        # 5. Step 5: Construct Structured Agent Result
        answer_source = "verified_corpus" if verification.is_verified else "curated_fallback"
        needs_more_info = research_output.get("status") in ["no_relevant_provision", "invalid"]

        return AgentResult(
            intent=classification.intent,
            domain=classification.domain,
            workflow=classification.workflow,
            verification=verification,
            answer_source=answer_source,
            confidence=verification.confidence,
            needs_more_information=needs_more_info,
            raw_response=research_output,
        )

