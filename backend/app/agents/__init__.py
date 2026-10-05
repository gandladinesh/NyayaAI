"""
NyayaAI - Phase 4 Agentic Legal Intelligence
Modular, cost-controlled agent architecture.
"""

from app.agents.query_classifier import (
    QueryClassifier,
    LegalDomain,
    QueryIntent,
    ClassificationResult,
)
from app.agents.orchestrator import AgentOrchestrator, AgentResult
from app.agents.legal_research_agent import LegalResearchAgent
from app.agents.action_agent import ActionAgent
from app.agents.verification_agent import VerificationAgent

__all__ = [
    "QueryClassifier",
    "LegalDomain",
    "QueryIntent",
    "ClassificationResult",
    "AgentOrchestrator",
    "AgentResult",
    "LegalResearchAgent",
    "ActionAgent",
    "VerificationAgent",
]

