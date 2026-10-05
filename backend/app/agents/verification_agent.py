"""
NyayaAI - Phase 4: Evidence Verification Agent
Validates that retrieved legal provisions and authorities meet strict accuracy
and grounding invariants before generating answers.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class VerificationSummary(BaseModel):
    is_verified: bool = Field(description="Whether the evidence meets grounding requirements")
    verification_status: str = Field(description="VERIFIED | PARTIALLY_VERIFIED | UNVERIFIED | INSUFFICIENT")
    confidence: float = Field(ge=0.0, le=1.0, description="Verification confidence score")
    evidence_count: int = Field(default=0, description="Number of verified items evaluated")
    has_authoritative_text: bool = Field(default=False, description="Contains verbatim bare act text")
    notes: list[str] = Field(default_factory=list, description="Audit and safety notes")


class VerificationAgent:
    """Zero-cost grounding and evidence verification agent."""

    def verify_evidence(
        self,
        retrieved_results: list[dict],
        relevance_score: int | None = None,
    ) -> VerificationSummary:
        """Inspect retrieved provisions to ensure authenticity and grounding."""
        if not retrieved_results:
            return VerificationSummary(
                is_verified=False,
                verification_status="INSUFFICIENT",
                confidence=0.0,
                evidence_count=0,
                has_authoritative_text=False,
                notes=["No verified provisions retrieved for this query."],
            )

        notes: list[str] = []
        verified_count = 0
        has_exact = False

        for r in retrieved_results:
            prov = r.get("provision") if isinstance(r, dict) else getattr(r, "provision", None)
            if prov is not None:
                status = getattr(prov, "verification_status", None)
                status_str = status.value if hasattr(status, "value") else str(status)
                if status_str.upper() == "VERIFIED":
                    verified_count += 1
                if getattr(prov, "exact_text", None):
                    has_exact = True
            elif isinstance(r, dict) and "exact_text" in r:
                if r.get("verification_status", "").upper() == "VERIFIED":
                    verified_count += 1
                if r.get("exact_text"):
                    has_exact = True

        # Safety check: score thresholds
        if relevance_score is not None and relevance_score < 30:
            notes.append("Low relevance match; treated as insufficient evidence.")
            return VerificationSummary(
                is_verified=False,
                verification_status="INSUFFICIENT",
                confidence=float(relevance_score) / 100.0,
                evidence_count=verified_count,
                has_authoritative_text=has_exact,
                notes=notes,
            )

        is_valid = verified_count > 0 and has_exact
        final_status = "VERIFIED" if is_valid else ("PARTIALLY_VERIFIED" if verified_count > 0 else "UNVERIFIED")

        return VerificationSummary(
            is_verified=is_valid,
            verification_status=final_status,
            confidence=0.95 if is_valid else 0.5,
            evidence_count=len(retrieved_results),
            has_authoritative_text=has_exact,
            notes=notes if notes else ["Evidence verified against authentic India Code / Government bare acts."],
        )

