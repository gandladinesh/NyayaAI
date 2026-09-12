from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.services.legal_provision_service import LegalProvisionService


router = APIRouter(
    prefix="/api/provisions",
    tags=["Legal Provisions"],
)

service = LegalProvisionService()


@router.get("")
async def get_provisions(
    search: Optional[str] = Query(default=None),
):
    """
    Return legal provisions from the verified local corpus.

    If search is provided, perform a Phase-1 keyword search.
    Otherwise, return all provisions.
    """
    if search:
        provisions = service.search(search)
    else:
        provisions = service.get_all()

    return {
        "count": len(provisions),
        "provisions": provisions,
    }


@router.get("/{provision_id}")
async def get_provision(provision_id: str):
    """Return a single legal provision by provision ID."""
    provision = service.get_by_id(provision_id)

    if provision is None:
        raise HTTPException(
            status_code=404,
            detail=f"Legal provision '{provision_id}' not found.",
        )

    return provision


@router.get("/reference/{reference_number}")
async def get_provision_by_reference(reference_number: str):
    """Return a provision by Article/Section reference number."""
    provision = service.get_by_reference(reference_number)

    if provision is None:
        raise HTTPException(
            status_code=404,
            detail=f"Legal provision '{reference_number}' not found.",
        )

    return provision