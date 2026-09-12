"""
NyayaAI — Case Authority Service

Loads curated judicial authorities and provides safe lookup
by case ID or legal provision.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from app.models.case_authority import CaseAuthority


class CaseAuthorityService:
    """Service for retrieving verified case authorities."""

    def __init__(self) -> None:
        self.corpus_path = (
            Path(__file__).resolve().parents[2]
            / "data"
            / "seed_case_authorities.json"
        )

        self._authorities: list[CaseAuthority] = []
        self._load_corpus()

    def _load_corpus(self) -> None:
        if not self.corpus_path.exists():
            raise FileNotFoundError(
                f"Case authority corpus not found: {self.corpus_path}"
            )

        with self.corpus_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("Invalid case authority corpus format.")

        self._authorities = [
            CaseAuthority.model_validate(record)
            for record in data
        ]

    def get_all(self) -> list[CaseAuthority]:
        return self._authorities.copy()

    def get_by_id(self, case_id: str) -> Optional[CaseAuthority]:
        for authority in self._authorities:
            if authority.case_id == case_id:
                return authority

        return None

    def get_for_provision(
        self,
        provision_id: str,
    ) -> list[CaseAuthority]:
        return [
            authority
            for authority in self._authorities
            if provision_id in authority.provision_ids
        ]