"""
API routes for States, Districts, and Authorities.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.models.authority import (
    StateRead,
    DistrictRead,
    AuthorityRead,
    AuthorityRoutingResult,
)
from app.services.authority_routing_service import AuthorityRoutingService

router = APIRouter(tags=["Authorities & Jurisdictions"])


@router.get(
    "/states",
    response_model=List[StateRead],
    summary="List all supported states and union territories",
    responses={
        200: {"description": "List of all states and UTs currently supported in NyayaAI"},
    }
)
async def list_states(session: AsyncSession = Depends(get_session)):
    """Fetch all supported Indian states and union territories.
    
    Returns basic information for each state including state code, capital, and high court details.
    Use state IDs from this endpoint to filter authorities and districts.
    
    **Currently supported states:** TS (Telangana), AP (Andhra Pradesh), MH (Maharashtra), DL (Delhi).
    """
    service = AuthorityRoutingService(session)
    states = await service.get_states()
    return [StateRead.model_validate(s) for s in states]


@router.get(
    "/states/{state_id}",
    response_model=StateRead,
    summary="Get details for a specific state",
    responses={
        200: {"description": "State details including capital, high court, and boundaries"},
        404: {"description": "State ID not found. Use /states to see supported states."},
    }
)
async def get_state(state_id: str, session: AsyncSession = Depends(get_session)):
    """Fetch detailed information for a specific state or union territory.
    
    Returns comprehensive information including state code, capital city, high court jurisdiction,
    and verification status.
    """
    service = AuthorityRoutingService(session)
    state = await service.get_state(state_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"State '{state_id}' not found.")
    return StateRead.model_validate(state)


@router.get(
    "/states/{state_id}/districts",
    response_model=List[DistrictRead],
    summary="List all districts in a state",
    responses={
        200: {"description": "List of all districts belonging to the specified state"},
        404: {"description": "State ID not found"},
    }
)
async def list_districts(state_id: str, session: AsyncSession = Depends(get_session)):
    """Fetch all districts belonging to a specific state.
    
    Returns district information including name, headquarters, and boundaries.
    Each district can have multiple authorities handling different legal categories.
    """
    service = AuthorityRoutingService(session)
    state = await service.get_state(state_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"State '{state_id}' not found.")
    districts = await service.get_districts_by_state(state_id)
    return [DistrictRead.model_validate(d) for d in districts]


@router.get(
    "/districts/{district_id}",
    response_model=DistrictRead,
    summary="Get details for a specific district",
    responses={
        200: {"description": "District information including headquarters and state"},
        404: {"description": "District ID not found"},
    }
)
async def get_district(district_id: str, session: AsyncSession = Depends(get_session)):
    """Fetch detailed information for a specific district.
    
    Returns district boundaries, headquarters, and administrative details.
    """
    service = AuthorityRoutingService(session)
    district = await service.get_district(district_id)
    if not district:
        raise HTTPException(status_code=404, detail=f"District '{district_id}' not found.")
    return DistrictRead.model_validate(district)


@router.get(
    "/authorities",
    response_model=List[AuthorityRead],
    summary="Search and filter authorities by jurisdiction and legal category",
    responses={
        200: {"description": "List of matching authorities with contact information"},
        400: {"description": "Invalid query parameters"},
    }
)
async def list_authorities(
    state_id: Optional[str] = Query(
        None,
        description="Filter by State code (e.g., 'TS', 'AP', 'MH', 'DL')"
    ),
    district_id: Optional[str] = Query(
        None,
        description="Filter by District code (e.g., 'TS-HYD', 'MH-MUM'). Implies state_id."
    ),
    legal_category: Optional[str] = Query(
        None,
        description="Filter by legal problem category (e.g., 'consumer_dispute', 'real_estate', 'legal_aid', 'human_rights')"
    ),
    session: AsyncSession = Depends(get_session)
):
    """Search authorities filtered by State, District, and Legal Category.
    
    Returns a list of authorities matched to your jurisdiction and problem type.
    Results NEVER include authorities outside the requested jurisdiction.
    
    **Typical usage:**
    1. Citizen selects a state → /authorities?state_id=TS
    2. Citizen selects a district → /authorities?state_id=TS&district_id=TS-HYD
    3. Citizen selects problem type → /authorities?state_id=TS&district_id=TS-HYD&legal_category=consumer_dispute
    4. For final routing, use /route endpoint for jurisdiction analysis + procedure details.
    """
    service = AuthorityRoutingService(session)
    authorities = await service.get_authorities(
        state_id=state_id,
        district_id=district_id,
        legal_category=legal_category
    )
    return [AuthorityRead.model_validate(a) for a in authorities]


@router.get(
    "/authorities/{authority_id}",
    summary="Get comprehensive details for an authority including contact and procedures",
    responses={
        200: {"description": "Comprehensive authority information with jurisdictions, complaint procedures, and escalation paths"},
        404: {"description": "Authority ID not found"},
    }
)
async def get_authority_detail(authority_id: str, session: AsyncSession = Depends(get_session)):
    """Fetch comprehensive details for an authority.
    
    Returns:
    - Official contact information (website, email, phone, address)
    - Jurisdiction description and scope
    - Complaint procedures and filing methods
    - Escalation authorities and appeal paths
    - Statutory time limits and fees
    - Verification status and source information
    
    This is the deep-dive endpoint for detailed authority information.
    For simple browsing, use /authorities with filters.
    """
    service = AuthorityRoutingService(session)
    data = await service.get_authority_detail(authority_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Authority '{authority_id}' not found.")
    return data


@router.get(
    "/route",
    response_model=AuthorityRoutingResult,
    summary="Route citizen to the correct authority (Action Mode)",
    responses={
        200: {"description": "Jurisdiction analysis with primary authority, escalation path, and complaint procedures"},
        400: {"description": "Missing required parameters (state_id, district_id)"},
        404: {"description": "Jurisdiction could not be determined — system requests more information"},
    }
)
async def route_jurisdiction(
    state_id: str = Query(
        ...,
        description="Required State code (e.g., 'TS', 'AP', 'MH', 'DL')"
    ),
    district_id: str = Query(
        ...,
        description="Required District code (e.g., 'TS-HYD', 'MH-MUM')"
    ),
    legal_category: Optional[str] = Query(
        None,
        description="Legal problem category (e.g., 'consumer_dispute', 'real_estate', 'legal_aid', 'human_rights')"
    ),
    session: AsyncSession = Depends(get_session)
):
    """NyayaAI Action Mode: Route citizen to the correct responsible authority.
    
    **Processing Pipeline:**
    1. Analyze jurisdiction (State → District → Category)
    2. Identify primary responsible authority
    3. Identify escalation/appellate authority
    4. Retrieve applicable laws and regulations
    5. Fetch statutory complaint procedures and filing instructions
    6. Compile step-by-step action roadmap for citizen
    
    **Response includes:**
    - `jurisdiction_analysis`: Whether jurisdiction was determined
    - `primary_authority`: The main forum to file complaint
    - `escalation_authority`: Where to appeal if primary forum fails
    - `complaint_procedure`: Statutory filing procedures and requirements
    - `applicable_central_laws`: Central laws applicable to this category
    - `applicable_state_laws`: State-specific laws and regulations
    - `action_plan_steps`: Step-by-step roadmap for the citizen
    
    **Note:** All contact information is from verified official sources.
    Citizens should verify current details on official website before visiting.
    """
    service = AuthorityRoutingService(session)
    return await service.route_action_query(
        state_id=state_id,
        district_id=district_id,
        legal_category=legal_category
    )
