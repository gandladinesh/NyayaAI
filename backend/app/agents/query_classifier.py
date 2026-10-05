"""
NyayaAI - Phase 4: Deterministic Query Classifier
Classifies incoming legal questions into domain, intent, and suggested workflow
without requiring paid LLM API calls.
"""

from __future__ import annotations

import re
from enum import Enum
from pydantic import BaseModel, Field


class LegalDomain(str, Enum):
    CONSTITUTIONAL = "constitutional"
    CRIMINAL = "criminal"
    CONSUMER = "consumer"
    CYBER = "cyber"
    EMPLOYMENT = "employment"
    PROPERTY = "property"
    FAMILY = "family"
    WOMEN_AND_CHILDREN = "women_and_children"
    HUMAN_RIGHTS = "human_rights"
    GOVERNMENT_SERVICES = "government_services"
    LEGAL_AID = "legal_aid"
    UNKNOWN = "unknown"


class QueryIntent(str, Enum):
    INFORMATIONAL = "informational"
    PROCEDURAL = "procedural"
    ACTION_ROUTING = "action_routing"
    UNKNOWN = "unknown"


class ClassificationResult(BaseModel):
    domain: LegalDomain = Field(description="Detected legal domain/category")
    intent: QueryIntent = Field(description="Detected user intent")
    workflow: str = Field(description="Selected agentic execution workflow")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Classification confidence")
    keywords_matched: list[str] = Field(default_factory=list, description="Keywords that triggered classification")
    suggested_category_filter: str | None = Field(default=None, description="Optional ProvisionCategory filter")


DOMAIN_PATTERNS: dict[LegalDomain, list[str]] = {
    LegalDomain.CONSTITUTIONAL: [
        r"\barticle\s+\d+[a-z]?\b",
        r"\bconstitution\b",
        r"\bfundamental\s+rights?\b",
        r"\bright\s+to\s+(life|equality|freedom|speech|liberty|education|privacy|religion)\b",
        r"\bwrit\b",
        r"\bhabeas\s+corpus\b",
        r"\bmandamus\b",
        r"\bquowarranto\b",
        r"\bprohibition\b",
        r"\bcertiorari\b",
        r"\bdirective\s+principles\b",
        r"\bdpsp\b",
        r"\buntouchability\b",
        r"\bpreventive\s+detention\b",
        r"\bdouble\s+jeopardy\b",
        r"\bself[\s-]incrimination\b",
    ],
    LegalDomain.CRIMINAL: [
        r"\b(bns|ipc|crpc|bnss)\b",
        r"\bsection\s+\d+[a-z]?\b",
        r"\btheft\b",
        r"\bmurder\b",
        r"\bcheating\b",
        r"\bfir\b",
        r"\bfirst\s+information\s+report\b",
        r"\bbail\b",
        r"\banticipatory\s+bail\b",
        r"\barrest\b",
        r"\bcustody\b",
        r"\bcriminal\b",
        r"\bassault\b",
        r"\brobbery\b",
        r"\bdacoity\b",
        r"\bextortion\b",
        r"\bforgery\b",
        r"\bdefamation\b",
        r"\bcriminal\s+intimidation\b",
        r"\bcriminal\s+breach\s+of\s+trust\b",
        r"\bconfession\b",
        r"\belectronic\s+evidence\b",
        r"\bbsa\b",
        r"\bevidence\b",
    ],
    LegalDomain.CONSUMER: [
        r"\bconsumer\b",
        r"\bdefective\s+(product|goods|item)\b",
        r"\bdeficiency\s+in\s+service\b",
        r"\brefund\b",
        r"\breplacement\b",
        r"\bovercharg(e|ing)\b",
        r"\bunfair\s+trade\s+practice\b",
        r"\bconsumer\s+forum\b",
        r"\bconsumer\s+court\b",
        r"\bdcdrc\b",
        r"\bconsumer\s+commission\b",
        r"\be-daakhil\b",
        r"\bnational\s+consumer\s+helpline\b",
        r"\b1915\b",
    ],
    LegalDomain.CYBER: [
        r"\bcyber\b",
        r"\bhack(ing|ed)?\b",
        r"\bonline\s+fraud\b",
        r"\bphishing\b",
        r"\botp\s+fraud\b",
        r"\bidentity\s+theft\b",
        r"\bcyber\s+bullying\b",
        r"\bdeepfake\b",
        r"\bit\s+act\b",
        r"\bcybercrime\.gov\.in\b",
        r"\b1930\b",
    ],
    LegalDomain.EMPLOYMENT: [
        r"\b(salary|wage|wages)\b",
        r"\bunpaid\s+salary\b",
        r"\btermination\b",
        r"\bwrongful\s+termination\b",
        r"\bprovident\s+fund\b",
        r"\bepf\b",
        r"\bepfo\b",
        r"\bgratuity\b",
        r"\blabour\b",
        r"\blabor\b",
        r"\blabour\s+court\b",
        r"\bworkplace\s+harassment\b",
        r"\bposh\b",
        r"\bminimum\s+wages\b",
    ],
    LegalDomain.PROPERTY: [
        r"\bproperty\b",
        r"\btenant\b",
        r"\blandlord\b",
        r"\bevict(ion)?\b",
        r"\brent\b",
        r"\brera\b",
        r"\bbuilder\b",
        r"\bdelayed\s+possession\b",
        r"\bflat\b",
        r"\bencroachment\b",
        r"\btitle\s+deed\b",
        r"\bregistration\b",
        r"\bpatta\b",
    ],
    LegalDomain.FAMILY: [
        r"\bdivorce\b",
        r"\bmaintenance\b",
        r"\balimony\b",
        r"\bchild\s+custody\b",
        r"\bmarriage\b",
        r"\bdomestic\s+violence\b",
        r"\bdowry\b",
        r"\bsection\s+125\b",
        r"\bsection\s+126\b",
        r"\bsection\s+85\b",
        r"\bsection\s+86\b",
        r"\b498a\b",
    ],
    LegalDomain.WOMEN_AND_CHILDREN: [
        r"\bwomen\b",
        r"\bchild\b",
        r"\bchildren\b",
        r"\bpocso\b",
        r"\bdomestic\s+violence\b",
        r"\bdowry\b",
        r"\bsexual\s+harassment\b",
        r"\bmaternity\b",
        r"\bjjt\b",
        r"\bjuvenile\b",
        r"\bncw\b",
        r"\bncpcr\b",
    ],
    LegalDomain.HUMAN_RIGHTS: [
        r"\bhuman\s+rights\b",
        r"\bnhrc\b",
        r"\bshrc\b",
        r"\bcustodial\s+(violence|death|torture)\b",
        r"\bpolice\s+(misconduct|excesses|brutality|harassment)\b",
        r"\billegal\s+detention\b",
    ],
    LegalDomain.GOVERNMENT_SERVICES: [
        r"\brti\b",
        r"\bright\s+to\s+information\b",
        r"\bpension\b",
        r"\bration\s+card\b",
        r"\baadhaar\b",
        r"\bvoter\s+id\b",
        r"\bpassport\b",
        r"\bgrievance\b",
        r"\bcpgrams\b",
    ],
    LegalDomain.LEGAL_AID: [
        r"\blegal\s+aid\b",
        r"\bfree\s+lawyer\b",
        r"\bdlsa\b",
        r"\bslsa\b",
        r"\bnalsa\b",
        r"\blok\s+adalat\b",
        r"\barticle\s+39a\b",
        r"\blegal\s+services\s+authority\b",
    ],
}

INTENT_PATTERNS: dict[QueryIntent, list[str]] = {
    QueryIntent.PROCEDURAL: [
        r"\bhow\s+to\s+(file|register|apply|get|obtain|claim|challenge|appeal)\b",
        r"\bprocedure\s+(for|to|of)\b",
        r"\bsteps?\s+(to|for)\b",
        r"\bprocess\s+(of|for|to)\b",
        r"\bhow\s+do\s+i\b",
        r"\bwhere\s+do\s+i\s+file\b",
        r"\bfiling\s+an?\s+fir\b",
        r"\bhow\s+is\s+an?\s+fir\b",
    ],
    QueryIntent.ACTION_ROUTING: [
        r"\bwhich\s+(authority|court|forum|department|officer|commission)\b",
        r"\bwho\s+(do\s+i\s+approach|is\s+responsible|handles)\b",
        r"\bwhere\s+to\s+(complain|report|file\s+case)\b",
        r"\bcontact\s+(dlsa|nhrc|shrc|rera|consumer\s+forum)\b",
    ],
    QueryIntent.INFORMATIONAL: [
        r"\bwhat\s+is\b",
        r"\bwhat\s+are\b",
        r"\bexplain\b",
        r"\bmeaning\s+of\b",
        r"\bdefinition\s+of\b",
        r"\bunder\s+(article|section|act|law)\b",
        r"\bpunishment\s+for\b",
        r"\bis\s+it\s+(legal|illegal|allowed|permitted)\b",
    ],
}


class QueryClassifier:
    """Zero-cost, deterministic query classifier for Indian legal questions."""

    def classify(self, query: str) -> ClassificationResult:
        normalized = query.lower().strip()

        if not normalized:
            return ClassificationResult(
                domain=LegalDomain.UNKNOWN,
                intent=QueryIntent.UNKNOWN,
                workflow="fallback_guidance",
                confidence=0.0,
                keywords_matched=[],
                suggested_category_filter=None,
            )

        # 1. Match domain
        matched_domain = LegalDomain.UNKNOWN
        matched_keywords: list[str] = []
        highest_domain_matches = 0

        for domain, patterns in DOMAIN_PATTERNS.items():
            matches = [p for p in patterns if re.search(p, normalized, re.IGNORECASE)]
            if len(matches) > highest_domain_matches:
                highest_domain_matches = len(matches)
                matched_domain = domain
                matched_keywords = matches

        # 2. Match intent
        matched_intent = QueryIntent.INFORMATIONAL
        for intent, patterns in INTENT_PATTERNS.items():
            if any(re.search(p, normalized, re.IGNORECASE) for p in patterns):
                matched_intent = intent
                break

        # 3. Determine workflow & suggested category filter
        suggested_category: str | None = None
        if matched_domain == LegalDomain.CONSTITUTIONAL:
            suggested_category = "constitution"
            workflow = "constitutional_legal_research"
        elif matched_domain == LegalDomain.CRIMINAL:
            if re.search(r"\b(bnss|procedure|fir|bail|arrest|custody)\b", normalized):
                suggested_category = "bnss"
            elif re.search(r"\b(bsa|evidence|confession|electronic)\b", normalized):
                suggested_category = "bsa"
            else:
                suggested_category = "bns"
            workflow = "criminal_legal_research"
        elif matched_domain == LegalDomain.CONSUMER:
            workflow = "consumer_grievance_workflow"
        elif matched_domain == LegalDomain.LEGAL_AID:
            workflow = "legal_aid_action_workflow"
        elif matched_intent == QueryIntent.ACTION_ROUTING:
            workflow = "action_mode_routing"
        elif matched_domain == LegalDomain.UNKNOWN:
            workflow = "general_legal_research"
        else:
            workflow = f"{matched_domain.value}_research"

        confidence = 1.0 if highest_domain_matches >= 2 else (0.8 if highest_domain_matches == 1 else 0.3)

        return ClassificationResult(
            domain=matched_domain,
            intent=matched_intent,
            workflow=workflow,
            confidence=confidence,
            keywords_matched=matched_keywords,
            suggested_category_filter=suggested_category,
        )

