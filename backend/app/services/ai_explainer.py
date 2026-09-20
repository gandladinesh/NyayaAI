"""
NyayaAI — AI Explanation Service

Gemini is used only to explain verified legal provisions
in simple language.

The AI must never generate or replace the exact legal text.
"""

from __future__ import annotations

from typing import Optional

from google import genai

from app.core.config import settings
from app.models.legal_provision import LegalProvision


# Human-readable language names for prompt clarity
_LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi (हिन्दी)",
    "te": "Telugu (తెలుగు)",
    "mr": "Marathi (मराठी)",
}


class AIExplainer:
    """Generate plain-language explanations from verified legal material."""

    def __init__(self) -> None:
        self.client: Optional[genai.Client] = None

        if settings.has_gemini:
            self.client = genai.Client(
                api_key=settings.gemini_api_key
            )

    def explain(
        self,
        question: str,
        provision: LegalProvision,
        language: str = "en",
    ) -> str:
        """
        Generate a simple explanation of a verified provision.

        Args:
            question: The citizen's legal question.
            provision: The verified legal provision to explain.
            language: ISO 639-1 code for the explanation language.
                      Supported: 'en', 'hi', 'te', 'mr'.
                      Defaults to 'en' (English).

        If Gemini is not configured, returns the curated English explanation
        already stored with the verified provision, regardless of language.

        The exact statutory text is NEVER altered, translated, or AI-generated.
        """

        if not settings.has_gemini or self.client is None:
            return provision.ai_explanation or (
                "An AI explanation is not currently available."
            )

        language_name = _LANGUAGE_NAMES.get(language, "English")
        language_instruction = (
            f"Respond ONLY in {language_name}."
            if language != "en"
            else "Respond in clear, simple English."
        )

        prompt = f"""
You are NyayaAI, an Indian legal information assistant.

Your task is to explain the verified legal provision below
in simple language for an ordinary citizen.

IMPORTANT RULES:
1. Do not change, rewrite, or reproduce the exact legal text.
2. Do not present your explanation as the legal text.
3. Do not invent legal rules, sections, authorities, cases, or facts.
4. Explain only what is reasonably supported by the supplied provision.
5. Clearly state that this is an AI-generated explanation.
6. Do not provide a definitive legal opinion.
7. If the question cannot be answered from the supplied provision,
   say so instead of guessing.
8. {language_instruction}
9. Keep the explanation concise (3-5 sentences).

User question:
{question}

Verified provision:
Reference: {provision.reference_number}
Act: {provision.act}
Exact legal text:
{provision.exact_text}

Provide a concise explanation in simple language.
"""

        try:
            response = self.client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
            )

            if response and response.text:
                return response.text.strip()
        except Exception:
            # On network timeout, quota exceeded, or upstream API error,
            # safely fall back to the curated, verified explanation without leaking errors.
            pass

        return (
            provision.ai_explanation
            or "An AI explanation is not currently available."
        )
