"""
NyayaAI — Revised Core Legal Provision Models (Phase 1)

ARCHITECTURE CONTRACT:
======================
`exact_text`     — verbatim from a verified official source. NEVER AI-generated.
`ai_explanation` — AI plain-language summary. NEVER the legal text. Always labeled.
`source_type`    — official | court | supplementary (IndianKanoon is NEVER "official")
`verification_status` — VERIFIED | PARTIALLY_VERIFIED | UNVERIFIED
Only VERIFIED provisions may display the green verified badge in the UI.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


# ── Enumerations ────────────────────────────────────────────────────────────

class ProvisionCategory(str, Enum):
    CONSTITUTION  = "constitution"
    IPC           = "ipc"          # Indian Penal Code 1860 — historical (pre 2024-07-01)
    BNS           = "bns"          # Bharatiya Nyaya Sanhita 2023 — current (from 2024-07-01)
    CRPC          = "crpc"         # CrPC 1973 — historical (pre 2024-07-01)
    BNSS          = "bnss"         # Bharatiya Nagarik Suraksha Sanhita 2023 — current
    CPC           = "cpc"          # Code of Civil Procedure 1908
    EVIDENCE_ACT  = "evidence_act" # Indian Evidence Act 1872 — historical
    BSA           = "bsa"          # Bharatiya Sakshya Adhiniyam 2023 — current
    STATE         = "state"        # State legislation
    OTHER         = "other"


class SourceType(str, Enum):
    """
    Source authority level.

    IMPORTANT: IndianKanoon MUST be labeled 'supplementary'.
    It must NEVER be labeled 'official' regardless of what it contains.
    Official sources are Government of India portals and ministry websites.
    Court sources are eCourts, SC/HC official portals.
    """
    OFFICIAL      = "official"      # India Code, eGazette, Ministry websites, GoI portals
    COURT         = "court"         # eCourts India, Supreme Court portal, HC portals
    SUPPLEMENTARY = "supplementary" # IndianKanoon, PRS, academic — reference only


class VerificationStatus(str, Enum):
    """
    Three-level verification status for exact_text.

    Only VERIFIED provisions display the green "✅ Verified Legal Text" badge.
    UNVERIFIED exact_text must be visually de-emphasized in the UI.
    """
    VERIFIED           = "verified"
    PARTIALLY_VERIFIED = "partially_verified"
    UNVERIFIED         = "unverified"


class TextSourceType(str, Enum):
    """How exact_text was obtained."""
    OFFICIAL_API       = "official_api"        # Live fetch from official government API
    INDIA_CODE_MANUAL  = "india_code_manual"   # Manually copied from indiacode.nic.in
    SEED_CORPUS        = "seed_corpus"         # From local curated seed JSON (Phase 1)
    HUGGINGFACE_DATASET= "huggingface_dataset" # From HuggingFace open dataset
    INDIAN_KANOON      = "indian_kanoon"       # From IndianKanoon API — supplementary
    MANUAL_ENTRY       = "manual_entry"        # Manually entered/verified


class JurisdictionScope(str, Enum):
    CENTRAL  = "central"   # Applies across all of India
    STATE    = "state"     # Applies to a specific state
    DISTRICT = "district"  # District-level jurisdiction
    LOCAL    = "local"     # Local body/municipality
    SPECIAL  = "special"   # Special tribunal/forum jurisdiction


# ── Core Legal Provision Model ───────────────────────────────────────────────

class LegalProvision(BaseModel):
    """
    Verified Indian legal provision with strict text/explanation separation.

    INVARIANTS:
    - exact_text is ALWAYS verbatim from an official/court source.
    - ai_explanation is ALWAYS AI-generated, labeled, and in a separate field.
    - They must NEVER be swapped, merged, or conflated at any layer.
    - source_type must reflect the actual source — IndianKanoon → supplementary.
    """

    # ── Identity ─────────────────────────────────────────────────────────────
    provision_id: str = Field(
        ...,
        description="Stable unique ID, e.g. 'constitution-india-article-21'",
    )
    provision_type: str = Field(
        default="CONSTITUTIONAL_ARTICLE",
        description="Type of legal provision, e.g. 'CONSTITUTIONAL_ARTICLE' or 'STATUTORY_SECTION'",
    )
    category: ProvisionCategory
    act: str = Field(..., description="Full act name, e.g. 'Constitution of India, 1950'")
    act_short: str = Field(..., description="Short citation, e.g. 'INDIA CONST.' or 'BNS 2023'")
    reference_number: str = Field(..., description="'Article 21' or 'Section 103'")
    article_number: Optional[str] = Field(None, description="Article number, e.g. '21' or '21A'")
    short_title: str = Field(..., description="Marginal title from the act")
    title: Optional[str] = Field(None, description="Heading/title from the act")
    part: Optional[str] = Field(None, description="Part/Chapter, e.g. 'Part III — Fundamental Rights'")
    clause: Optional[str] = Field(None, description="Specific clause if applicable")

    # ── EXACT VERBATIM LEGAL TEXT — NEVER AI-GENERATED ───────────────────────
    exact_text: str = Field(
        ...,
        description=(
            "Verbatim text from an official source. "
            "MUST NOT be AI-generated. "
            "MUST come from source_url or text_source. "
            "Any consumer of this field must treat it as source text only."
        ),
    )
    exact_text_language: str = Field(default="en", description="ISO 639-1 language code")
    language: str = Field(default="English", description="Language of provision")

    # ── AI EXPLANATION — NEVER THE LEGAL TEXT ────────────────────────────────
    ai_explanation: Optional[str] = Field(
        None,
        description=(
            "AI-generated plain-language explanation. "
            "This is NOT the legal text. "
            "Must ALWAYS be labeled as AI explanation in any output or UI. "
            "Generated by explaining exact_text — never generated from LLM memory alone."
        ),
    )

    # ── Source & Authority ────────────────────────────────────────────────────
    source_name: str = Field(..., description="E.g. 'Ministry of Law and Justice, GoI'")
    source_type: SourceType = Field(..., description="official | court | supplementary")
    source_authority: str = Field(
        ...,
        description="E.g. 'Government of India' | 'Supreme Court of India' | 'IndianKanoon'",
    )
    source_url: str = Field(..., description="Direct URL to the provision in its official source")
    indiankanoon_url: Optional[str] = Field(
        None,
        description="IndianKanoon reference URL — supplementary/reference only, never authoritative",
    )

    # ── Citation ──────────────────────────────────────────────────────────────
    official_citation: str = Field(
        ...,
        description="Standard citation, e.g. 'INDIA CONST. art. 21' or 'BNS 2023, s. 103'",
    )
    citation: Optional[str] = Field(None, description="Citation reference, e.g. 'INDIA CONST. art. 21'")

    # ── Verification ──────────────────────────────────────────────────────────
    verification_status: VerificationStatus = Field(
        default=VerificationStatus.UNVERIFIED,
        description=(
            "VERIFIED = text confirmed against official source. "
            "PARTIALLY_VERIFIED = official source used but not cross-checked. "
            "UNVERIFIED = seed/supplementary source only."
        ),
    )
    text_source: TextSourceType = Field(default=TextSourceType.SEED_CORPUS)
    last_verified: date = Field(..., description="Date exact_text was last verified")

    # ── Versioning & Effective Dates ──────────────────────────────────────────
    effective_date: Optional[date] = Field(None, description="Date provision came into force")
    effective_from: Optional[date] = Field(None, description="Effective from date")
    effective_to: Optional[date] = Field(None, description="Effective to date if repealed/amended")
    is_current_law: bool = Field(
        default=True,
        description="False for historical provisions superseded by newer legislation",
    )
    supersedes: Optional[str] = Field(
        None,
        description="Provision ID this replaced (e.g. BNS s.103 supersedes IPC s.302)",
    )
    superseded_by: Optional[str] = Field(
        None,
        description="Provision ID that replaced this (e.g. IPC s.302 superseded by BNS s.103)",
    )
    version_note: Optional[str] = Field(
        None,
        description="E.g. 'As amended by 42nd Constitutional Amendment, 1976'",
    )
    amendments: List[str] = Field(default_factory=list)

    # ── Jurisdiction ──────────────────────────────────────────────────────────
    jurisdiction: JurisdictionScope = Field(default=JurisdictionScope.CENTRAL)
    applicable_states: List[str] = Field(
        default_factory=list,
        description="Empty = all India. Else list of state_ids, e.g. ['MH', 'TS']",
    )

    # ── Relations ─────────────────────────────────────────────────────────────
    related_provisions: List[str] = Field(default_factory=list)

    # ── Safety validator ──────────────────────────────────────────────────────
    @model_validator(mode="after")
    def enforce_text_separation(self) -> "LegalProvision":
        """
        Runtime guard: ai_explanation must never equal exact_text.
        Prevents accidental conflation of legal source text and AI output.
        """
        if (
            self.ai_explanation
            and self.ai_explanation.strip() == self.exact_text.strip()
        ):
            raise ValueError(
                "ARCHITECTURE VIOLATION: ai_explanation is identical to exact_text. "
                "The AI explanation must be a distinct plain-language summary — "
                "not a copy of the original legal text."
            )
        return self

    @model_validator(mode="after")
    def enforce_source_type_consistency(self) -> "LegalProvision":
        """
        Guard: Indian Kanoon sources must never be labeled 'official'.
        """
        if (
            "indiankanoon" in self.source_url.lower()
            and self.source_type == SourceType.OFFICIAL
        ):
            raise ValueError(
                "ARCHITECTURE VIOLATION: IndianKanoon source_url cannot have source_type='official'. "
                "IndianKanoon is a supplementary reference source. "
                "Use source_type='supplementary'."
            )
        return self


# ── Evidence Section (wraps provisions in an AI response) ───────────────────

class LegalEvidenceSection(BaseModel):
    """
    Structured evidence section embedded in every AI response.
    The provisions list is always separate from the AI answer text.
    """
    section_title: str = Field(default="Legal Text / Evidence")
    provisions: List[LegalProvision]
    query_context: Optional[str] = None
    coverage_note: Optional[str] = Field(
        None,
        description=(
            "E.g. 'Phase 1 corpus covers ~30 Constitution articles and 15 BNS sections. "
            "Additional acts will be added in future phases.'"
        ),
    )


# ── Query / Response Models ──────────────────────────────────────────────────

class QueryMode(str, Enum):
    INFORMATION = "information"  # No mandatory location; legal Q&A
    ACTION      = "action"       # Full State→District→Authority routing


class InformationQuery(BaseModel):
    question: str
    mode: QueryMode = QueryMode.INFORMATION
    state_id: Optional[str] = None        # Optional context
    district_id: Optional[str] = None
    incident_date: Optional[date] = None  # For historical law selection


class ActionQuery(BaseModel):
    question: str
    mode: QueryMode = QueryMode.ACTION
    state_id: str = Field(..., description="Required for Action Mode")
    district_id: str = Field(..., description="Required for Action Mode")
    legal_category: Optional[str] = None
    incident_date: Optional[date] = None
    clarifying_answers: Optional[dict] = None


class ClarifyingQuestion(BaseModel):
    """A jurisdiction-aware clarifying question before routing to an authority."""
    question_id: str
    question_text: str
    options: Optional[List[str]] = None
    required: bool = True


class AIQueryResponse(BaseModel):
    """
    Complete response from /api/query.
    answer and evidence are always separate top-level fields.
    """
    query_id: str
    mode: QueryMode
    answer: str = Field(
        ...,
        description=(
            "AI-generated answer. This is AI output — not legal text. "
            "Citations appear as inline references, e.g. [Article 21]."
        ),
    )
    evidence: LegalEvidenceSection
    clarifying_questions: List[ClarifyingQuestion] = Field(default_factory=list)
    disclaimer: str = Field(
        default=(
            "This response is generated by AI for informational purposes only. "
            "The exact legal text shown is sourced from official documents. "
            "Always verify the current version of any law before relying on it. "
            "This does not constitute legal advice."
        ),
    )
    law_version_note: Optional[str] = Field(
        None,
        description=(
            "E.g. 'BNS 2023 applies to offences from 1 July 2024. "
            "IPC 1860 applies to pre-2024 offences.'"
        ),
    )


class ProvisionSearchResult(BaseModel):
    """Lightweight search result stub before fetching full provision."""
    provision_id: str
    reference_number: str
    short_title: str
    act: str
    category: ProvisionCategory
    official_citation: str
    verification_status: VerificationStatus
    source_type: SourceType
    is_current_law: bool
    relevance_score: Optional[float] = None
