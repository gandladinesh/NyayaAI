from enum import Enum
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.models.legal_provision import ProvisionCategory
from app.services.legal_query_service import LegalQueryService


class ExplanationLanguage(str, Enum):
    """Supported languages for AI-generated plain-language explanations.

    The exact statutory legal text is always returned in English
    (the authoritative language of the enactment).
    Only AI explanations are rendered in the requested language.
    """
    ENGLISH  = "en"
    HINDI    = "hi"
    TELUGU   = "te"
    MARATHI  = "mr"


class QueryRequest(BaseModel):
    """Query request for legal information lookup.
    
    Combines RAG retrieval over verified legal corpus with AI explanations.
    """
    question: str = Field(
        min_length=1,
        max_length=2000,
        description="The legal question or topic to search for (1-2000 characters)",
        json_schema_extra={"example": "What is the right to life guaranteed under the Indian Constitution?"}
    )
    category: Optional[ProvisionCategory] = Field(
        default=None,
        description="Optional legal category to filter results (e.g., 'constitution', 'bns', 'ipc')"
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Number of top legal provisions to retrieve and explain (1-5)"
    )
    language: ExplanationLanguage = Field(
        default=ExplanationLanguage.ENGLISH,
        description=(
            "Language for AI-generated plain-language explanation. "
            "Supported: 'en' (English), 'hi' (Hindi), 'te' (Telugu), 'mr' (Marathi). "
            "The exact statutory legal text is always in English regardless of this setting."
        ),
    )


router = APIRouter(
    prefix="/api/query",
    tags=["Legal Query"],
)

service = LegalQueryService()


@router.post(
    "",
    summary="Query legal information and get AI-explained provisions",
    responses={
        200: {"description": "Legal query answered with verified provisions and AI explanations"},
        400: {"description": "Invalid request (empty question, invalid top_k, etc.)"},
    }
)
async def query_legal(request: QueryRequest):
    """Search NyayaAI for verified Indian legal provisions matching your question.
    
    This endpoint performs semantic RAG (Retrieval-Augmented Generation) over verified legal corpus.
    Returns the top-k matching provisions with exact legal text and AI explanations.
    
    **Response contains:**
    - `status`: 'success', 'no_relevant_provision', or 'invalid'
    - `primary_result`: Main provision matching the query (if found)
    - `related_results`: Additional related provisions
    - `question`: Echoed query for confirmation
    - `language`: Language used for AI explanations
    
    **Multilingual explanations:**
    Set `language` to `'hi'` (Hindi), `'te'` (Telugu), or `'mr'` (Marathi) to receive
    AI-generated plain-language explanations in that language.
    The exact statutory legal text is always returned verbatim in English.
    
    **Note:** Exact legal text is NEVER AI-generated. AI explanations are clearly labeled.
    """
    return service.answer(
        question=request.question,
        category=request.category,
        top_k=request.top_k,
        language=request.language.value,
    )