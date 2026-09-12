from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.models.legal_provision import ProvisionCategory
from app.services.legal_query_service import LegalQueryService


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    category: Optional[ProvisionCategory] = None
    top_k: int = Field(default=3, ge=1, le=5)


router = APIRouter(
    prefix="/api/query",
    tags=["Legal Query"],
)

service = LegalQueryService()


@router.post("")
async def query_legal(request: QueryRequest):
    return service.answer(
        question=request.question,
        category=request.category,
        top_k=request.top_k,
    )