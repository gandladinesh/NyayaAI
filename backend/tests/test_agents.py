"""
Automated tests for Phase 4: Agent Orchestrator, Query Classifier,
Verification Agent, and Legal Research Agent.
"""

import pytest
from app.agents.query_classifier import QueryClassifier, LegalDomain, QueryIntent
from app.agents.verification_agent import VerificationAgent, VerificationSummary
from app.agents.orchestrator import AgentOrchestrator, AgentResult
from app.agents.legal_research_agent import LegalResearchAgent
from app.models.legal_provision import ProvisionCategory
from app.services.legal_query_service import LegalQueryService


@pytest.fixture
def classifier():
    return QueryClassifier()


@pytest.fixture
def verification_agent():
    return VerificationAgent()


@pytest.fixture
def orchestrator():
    return AgentOrchestrator()


# -------------------------------------------------------------------------
# 1. Constitutional Query Classification
# -------------------------------------------------------------------------

def test_constitutional_query_classification(classifier):
    res = classifier.classify("What is the right to life under Article 21?")
    assert res.domain == LegalDomain.CONSTITUTIONAL
    assert res.intent == QueryIntent.INFORMATIONAL
    assert res.workflow == "constitutional_legal_research"
    assert res.suggested_category_filter == "constitution"
    assert res.confidence >= 0.8

    res2 = classifier.classify("How does writ of habeas corpus protect personal liberty?")
    assert res2.domain == LegalDomain.CONSTITUTIONAL
    assert len(res2.keywords_matched) > 0


# -------------------------------------------------------------------------
# 2. Criminal Query Classification
# -------------------------------------------------------------------------

def test_criminal_query_classification(classifier):
    res = classifier.classify("What is the punishment for theft under BNS Section 303?")
    assert res.domain == LegalDomain.CRIMINAL
    assert res.workflow == "criminal_legal_research"
    assert res.suggested_category_filter == "bns"

    res_proc = classifier.classify("How is an FIR filed under BNSS Section 173?")
    assert res_proc.domain == LegalDomain.CRIMINAL
    assert res_proc.intent == QueryIntent.PROCEDURAL
    assert res_proc.suggested_category_filter == "bnss"

    res_evid = classifier.classify("Is electronic record admissible as primary evidence under BSA?")
    assert res_evid.domain == LegalDomain.CRIMINAL
    assert res_evid.suggested_category_filter == "bsa"


# -------------------------------------------------------------------------
# 3. Consumer Query Classification
# -------------------------------------------------------------------------

def test_consumer_query_classification(classifier):
    res = classifier.classify("I bought a defective product and seller refused refund. How to file consumer complaint?")
    assert res.domain == LegalDomain.CONSUMER
    assert res.workflow == "consumer_grievance_workflow"


# -------------------------------------------------------------------------
# 4. Unknown Query Classification
# -------------------------------------------------------------------------

def test_unknown_query_classification(classifier):
    res = classifier.classify("xyzabc foobar random words 12345")
    assert res.domain == LegalDomain.UNKNOWN
    assert res.workflow == "general_legal_research"
    assert res.confidence < 0.5

    res_empty = classifier.classify("   ")
    assert res_empty.domain == LegalDomain.UNKNOWN
    assert res_empty.intent == QueryIntent.UNKNOWN


# -------------------------------------------------------------------------
# 5. Orchestrator Routing & Pipeline Execution
# -------------------------------------------------------------------------

def test_orchestrator_pipeline_execution(orchestrator):
    result: AgentResult = orchestrator.execute_agent_pipeline(
        question="What is the right to life guaranteed under the Indian Constitution?",
        language="en"
    )

    assert isinstance(result, AgentResult)
    assert result.domain == LegalDomain.CONSTITUTIONAL
    assert result.verification.is_verified is True
    assert result.verification.verification_status == "VERIFIED"
    assert result.answer_source == "verified_corpus"
    assert result.needs_more_information is False
    assert result.raw_response["status"] == "success"
    assert result.raw_response["primary_result"] is not None


# -------------------------------------------------------------------------
# 6. No-Gemini Operation Safety
# -------------------------------------------------------------------------

def test_orchestrator_no_gemini_fallback(orchestrator):
    # Ensure pipeline works smoothly without any active Gemini LLM
    result = orchestrator.handle_query(
        question="What is theft under BNS?",
        language="en"
    )

    assert result["status"] == "success"
    assert result["primary_result"]["exact_text"] is not None
    assert result["primary_result"]["ai_explanation"] is not None
    assert len(result["primary_result"]["exact_text"]) > 0


# -------------------------------------------------------------------------
# 7. Insufficient-Evidence Safety Behavior
# -------------------------------------------------------------------------

def test_orchestrator_insufficient_evidence_behavior(orchestrator):
    result: AgentResult = orchestrator.execute_agent_pipeline(
        question="xyzzy_completely_fake_law_nonexistent_concept_99999"
    )

    assert isinstance(result, AgentResult)
    # When evidence is insufficient or no provision matches
    if result.raw_response["status"] == "no_relevant_provision":
        assert result.needs_more_information is True
        assert result.verification.is_verified is False
        assert result.raw_response["suggestions"] is not None
        assert result.raw_response["next_steps"] is not None


# -------------------------------------------------------------------------
# 8. Existing LegalQueryService Compatibility
# -------------------------------------------------------------------------

def test_legal_query_service_compatibility():
    service = LegalQueryService()
    res = service.answer(
        question="What is bail under BNSS?",
        category=ProvisionCategory.BNSS,
    )
    assert res["status"] == "success"
    assert "relevance_score" in res["primary_result"]
    assert "confidence_level" in res["primary_result"]

