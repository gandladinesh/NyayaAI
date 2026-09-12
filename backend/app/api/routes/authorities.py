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


@router.get("/states", response_model=List[StateRead])
async def list_states(session: AsyncSession = Depends(get_session)):
    """Fetch all supported states and union territories."""
    service = AuthorityRoutingService(session)
    states = await service.get_states()
    return [StateRead.model_validate(s) for s in states]


@router.get("/states/{state_id}", response_model=StateRead)
async def get_state(state_id: str, session: AsyncSession = Depends(get_session)):
    """Fetch details of a specific state/UT by state code."""
    service = AuthorityRoutingService(session)
    state = await service.get_state(state_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"State '{state_id}' not found.")
    return StateRead.model_validate(state)


@router.get("/states/{state_id}/districts", response_model=List[DistrictRead])
async def list_districts(state_id: str, session: AsyncSession = Depends(get_session)):
    """Fetch all districts belonging to a specific state."""
    service = AuthorityRoutingService(session)
    state = await service.get_state(state_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"State '{state_id}' not found.")
    districts = await service.get_districts_by_state(state_id)
    return [DistrictRead.model_validate(d) for d in districts]


@router.get("/districts/{district_id}", response_model=DistrictRead)
async def get_district(district_id: str, session: AsyncSession = Depends(get_session)):
    """Fetch details of a specific district by district code."""
    service = AuthorityRoutingService(session)
    district = await service.get_district(district_id)
    if not district:
        raise HTTPException(status_code=404, detail=f"District '{district_id}' not found.")
    return DistrictRead.model_validate(district)


@router.get("/authorities", response_model=List[AuthorityRead])
async def list_authorities(
    state_id: Optional[str] = Query(None, description="State ID (e.g. 'TS', 'AP', 'MH', 'DL')"),
    district_id: Optional[str] = Query(None, description="District ID (e.g. 'TS-HYD')"),
    legal_category: Optional[str] = Query(None, description="e.g. 'consumer_dispute', 'real_estate', 'legal_aid'"),
    session: AsyncSession = Depends(get_session)
):
    """
    List authorities filtered by State, District, and/or Legal Category.
    Never returns authorities outside the requested jurisdiction.
    """
    service = AuthorityRoutingService(session)
    authorities = await service.get_authorities(
        state_id=state_id,
        district_id=district_id,
        legal_category=legal_category
    )
    return [AuthorityRead.model_validate(a) for a in authorities]


@router.get("/authorities/{authority_id}")
async def get_authority_detail(authority_id: str, session: AsyncSession = Depends(get_session)):
    """
    Fetch comprehensive details for an authority including official contact,
    jurisdictions, complaint procedures, and escalation paths.
    """
    service = AuthorityRoutingService(session)
    data = await service.get_authority_detail(authority_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Authority '{authority_id}' not found.")
    return data


@router.get("/route", response_model=AuthorityRoutingResult)
async def route_jurisdiction(
    state_id: str = Query(..., description="Required State ID"),
    district_id: str = Query(..., description="Required District ID"),
    legal_category: Optional[str] = Query(None, description="Legal problem category"),
    session: AsyncSession = Depends(get_session)
):
    """
    Action Mode Authority Routing Pipeline:
    State -> District -> Problem -> Jurisdiction Analysis -> Responsible Authority -> Complaint -> Escalation.
    """
    service = AuthorityRoutingService(session)
    return await service.route_action_query(
        state_id=state_id,
        district_id=district_id,
        legal_category=legal_category
    )
