"""
NyayaAI — Case Authority Model

Stores authoritative judicial decisions that support
interpretations of verified legal provisions.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class CaseAuthority(BaseModel):
    """A verified judicial authority supporting a legal interpretation."""

    case_id: str = Field(min_length=1)
    case_name: str = Field(min_length=1)
    citation: str = Field(min_length=1)

    court: str = Field(min_length=1)
    judgment_date: Optional[date] = None

    provision_ids: list[str] = Field(default_factory=list)

    legal_principle: str = Field(min_length=1)

    source_name: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    source_url: str = Field(min_length=1)

    verification_status: str = Field(default="verified")