"""
NyayaAI - Phase 4: Action Agent
Connects citizens to appropriate administrative or statutory redressal pathways,
responsible authorities, and procedural filing steps.
"""

from __future__ import annotations

from typing import Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from app.services.authority_routing_service import AuthorityRoutingService


class ActionAgent:
    """Specialized agent for jurisdictional analysis and authority action routing."""

    def __init__(self, session: Optional[AsyncSession] = None) -> None:
        self.session = session

    async def route_grievance(
        self,
        session: AsyncSession,
        state_id: str,
        district_id: str,
        legal_category: str,
    ) -> dict:
        """Route grievance to designated official authority and return procedural roadmap."""
        active_session = self.session or session
        routing_service = AuthorityRoutingService(active_session)
        return await routing_service.route_grievance(
            state_id=state_id,
            district_id=district_id,
            legal_category=legal_category,
        )

