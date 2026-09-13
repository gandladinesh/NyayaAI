from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.legal_provision import ProvisionCategory
from app.services.legal_provision_service import LegalProvisionService


router = APIRouter(
    prefix="/api/provisions",
    tags=["Legal Provisions"],
)

service = LegalProvisionService()


@router.get(
    "",
    summary="Browse legal provisions or search with keywords",
    responses={
        200: {"description": "List of legal provisions (optionally filtered by search query and category)"},
        400: {"description": "Invalid search query"},
    }
)
async def get_provisions(
    search: Optional[str] = Query(
        default=None,
        description="Optional keyword search (e.g., 'right to life', 'bail', 'arrest', 'theft'). Performs keyword-based lookup across provision titles and text.",
    ),
    category: Optional[ProvisionCategory] = Query(
        default=None,
        description="Optional category filter (e.g., 'constitution', 'bns', 'bnss', 'bsa')",
    ),
):
    """Browse verified legal provisions or search by keyword.
    
    **Modes:**
    1. **Browse all:** Call without `search` parameter to list all verified provisions in corpus
    2. **Keyword search:** Provide `search` parameter to find provisions matching keywords
    
    **Response format:**
    ```json
    {
      "count": 42,
      "provisions": [... array of LegalProvision objects ...]
    }
    ```
    
    **Note:** This is a Phase-1 implementation using keyword search.
    For semantic search with AI explanations, use the /api/query endpoint instead.
    """
    if search:
        provisions = service.search(search, category=category)
    elif category:
        provisions = [p for p in service.get_all() if p.category == category]
    else:
        provisions = service.get_all()

    return {
        "count": len(provisions),
        "provisions": provisions,
    }


@router.get(
    "/{provision_id}",
    summary="Get details of a specific legal provision",
    responses={
        200: {"description": "Complete provision information including exact legal text and source details"},
        404: {"description": "Provision ID not found in corpus"},
    }
)
async def get_provision(provision_id: str):
    """Fetch detailed information for a specific legal provision.
    
    Returns:
    - Full provision text from verified official source
    - Category and classification (Constitution, IPC, BNS, etc.)
    - Citation information
    - Source reference and verification status
    - Related case authorities where applicable
    
    **Verification:**
    - VERIFIED provisions have official text from government sources
    - PARTIALLY_VERIFIED provisions may have minor formatting changes
    - UNVERIFIED provisions need additional validation
    """
    provision = service.get_by_id(provision_id)

    if provision is None:
        raise HTTPException(
            status_code=404,
            detail=f"Legal provision '{provision_id}' not found.",
        )

    return provision


@router.get(
    "/reference/{reference_number}",
    summary="Get legal provision by reference number or citation",
    responses={
        200: {"description": "Legal provision matching reference number or citation"},
        404: {"description": "Provision reference not found"},
    }
)
async def get_provision_by_reference(
    reference_number: str,
    category: Optional[ProvisionCategory] = Query(
        default=None,
        description="Optional category filter to disambiguate across Acts (e.g. 'bnss', 'bsa')",
    ),
):
    """Return a provision by Article/Section reference number or official citation."""
    provision = service.get_by_reference(reference_number, category=category)

    if provision is None:
        raise HTTPException(
            status_code=404,
            detail=f"Legal provision '{reference_number}' not found.",
        )

    return provision