"""
Authority Routing Service.
Executes the State -> District -> Problem -> Jurisdiction -> Responsible Authority -> Complaint -> Escalation pipeline.
"""

from typing import Optional, List
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.authority import (
    State,
    District,
    Authority,
    AuthorityRead,
    AuthorityJurisdiction,
    ComplaintProcedure,
    EscalationPath,
    JurisdictionAnalysis,
    AuthorityRoutingResult,
    AuthorityLevel,
)


class AuthorityRoutingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_states(self) -> List[State]:
        """Fetch all supported states/UTs."""
        stmt = select(State).order_by(State.state_name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_state(self, state_id: str) -> Optional[State]:
        """Fetch a state by ID."""
        return await self.session.get(State, state_id.upper())

    async def get_districts_by_state(self, state_id: str) -> List[District]:
        """Fetch all districts belonging to a specific state."""
        stmt = select(District).where(District.state_id == state_id.upper()).order_by(District.district_name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_district(self, district_id: str) -> Optional[District]:
        """Fetch a district by ID."""
        return await self.session.get(District, district_id)

    async def get_authorities(
        self,
        state_id: Optional[str] = None,
        district_id: Optional[str] = None,
        legal_category: Optional[str] = None,
    ) -> List[Authority]:
        """
        Query authorities filtered by State, District, and/or legal category.
        Ensures strict jurisdiction matching without returning out-of-jurisdiction bodies.
        """
        stmt = select(Authority).where(Authority.is_active == True)

        if district_id:
            # District authority matching this district OR state/central authority covering it
            stmt = stmt.where(
                (Authority.district_id == district_id) |
                ((Authority.state_id == state_id) & (Authority.district_id.is_(None))) |
                (Authority.authority_level == AuthorityLevel.CENTRAL)
            )
        elif state_id:
            # State authority or central authority
            stmt = stmt.where(
                (Authority.state_id == state_id.upper()) |
                (Authority.authority_level == AuthorityLevel.CENTRAL)
            )

        if legal_category:
            stmt = stmt.join(AuthorityJurisdiction).where(
                AuthorityJurisdiction.legal_category == legal_category.lower()
            )

        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_authority_detail(self, authority_id: str) -> Optional[dict]:
        """Get authority details including complaint procedures and escalation paths."""
        authority = await self.session.get(Authority, authority_id)
        if not authority:
            return None

        # Fetch jurisdictions
        j_stmt = select(AuthorityJurisdiction).where(AuthorityJurisdiction.authority_id == authority_id)
        j_res = await self.session.execute(j_stmt)
        jurisdictions = list(j_res.scalars().all())

        # Fetch procedures
        p_stmt = select(ComplaintProcedure).where(ComplaintProcedure.authority_id == authority_id)
        p_res = await self.session.execute(p_stmt)
        procedures = list(p_res.scalars().all())

        # Fetch escalation paths (outgoing)
        e_stmt = select(EscalationPath).where(EscalationPath.from_authority_id == authority_id)
        e_res = await self.session.execute(e_stmt)
        escalations = list(e_res.scalars().all())

        return {
            "authority": authority,
            "jurisdictions": jurisdictions,
            "complaint_procedures": procedures,
            "escalation_paths": escalations,
        }

    async def route_action_query(
        self,
        state_id: str,
        district_id: str,
        legal_category: Optional[str] = None,
    ) -> AuthorityRoutingResult:
        """
        Full jurisdiction routing pipeline:
        State -> District -> Legal Category -> Jurisdiction Analysis -> Responsible Authority -> Complaint -> Escalation
        """
        # Validate State & District
        state = await self.get_state(state_id)
        if not state:
            return AuthorityRoutingResult(
                jurisdiction_analysis=JurisdictionAnalysis(
                    is_determined=False,
                    reasoning=f"State '{state_id}' is not indexed in NyayaAI.",
                    missing_information="Please select a valid supported State (Telangana, Andhra Pradesh, Maharashtra, or Delhi)."
                )
            )

        district = await self.get_district(district_id)
        if not district or district.state_id != state.state_id:
            return AuthorityRoutingResult(
                jurisdiction_analysis=JurisdictionAnalysis(
                    is_determined=False,
                    reasoning=f"District '{district_id}' is not recognized under state '{state.state_name}'.",
                    missing_information="Please select a valid District belonging to the selected State."
                )
            )

        if not legal_category:
            return AuthorityRoutingResult(
                jurisdiction_analysis=JurisdictionAnalysis(
                    is_determined=False,
                    reasoning=f"Location verified as {district.district_name}, {state.state_name}. However, legal problem category was not provided.",
                    missing_information="Please specify the legal problem category (e.g. 'consumer_dispute', 'real_estate', 'legal_aid', 'human_rights') to determine the responsible authority."
                )
            )

        category = legal_category.lower().strip()

        # Step 1: Look for exact District-level authority first
        district_auth_stmt = (
            select(Authority)
            .join(AuthorityJurisdiction)
            .where(
                Authority.district_id == district.district_id,
                Authority.authority_level == AuthorityLevel.DISTRICT,
                AuthorityJurisdiction.legal_category == category,
                Authority.is_active == True,
            )
        )
        res = await self.session.execute(district_auth_stmt)
        primary_auth = res.scalars().first()

        # Step 2: If no district-level authority, look for State-level authority
        if not primary_auth:
            state_auth_stmt = (
                select(Authority)
                .join(AuthorityJurisdiction)
                .where(
                    Authority.state_id == state.state_id,
                    Authority.authority_level == AuthorityLevel.STATE,
                    AuthorityJurisdiction.legal_category == category,
                    Authority.is_active == True,
                )
            )
            res = await self.session.execute(state_auth_stmt)
            primary_auth = res.scalars().first()

        # Step 3: If no state-level authority, check for Central Authority
        if not primary_auth:
            central_auth_stmt = (
                select(Authority)
                .join(AuthorityJurisdiction)
                .where(
                    Authority.authority_level == AuthorityLevel.CENTRAL,
                    AuthorityJurisdiction.legal_category == category,
                    Authority.is_active == True,
                )
            )
            res = await self.session.execute(central_auth_stmt)
            primary_auth = res.scalars().first()

        if not primary_auth:
            return AuthorityRoutingResult(
                jurisdiction_analysis=JurisdictionAnalysis(
                    is_determined=False,
                    reasoning=f"No verified authority in Phase 1 database matches category '{category}' for {district.district_name}, {state.state_name}.",
                    missing_information=f"Authority records for '{category}' in this jurisdiction are being indexed in future phases."
                )
            )

        # Convert to AuthorityRead
        primary_read = AuthorityRead.model_validate(primary_auth)

        # Step 4: Look up Complaint Procedure
        proc_stmt = select(ComplaintProcedure).where(
            ComplaintProcedure.authority_id == primary_auth.authority_id,
            ComplaintProcedure.legal_category == category,
        )
        proc_res = await self.session.execute(proc_stmt)
        procedure = proc_res.scalars().first()

        # Step 5: Look up Escalation Authority
        escalation_read = None
        esc_stmt = select(EscalationPath).where(
            EscalationPath.from_authority_id == primary_auth.authority_id,
            EscalationPath.legal_category == category,
        )
        esc_res = await self.session.execute(esc_stmt)
        esc_path = esc_res.scalars().first()

        if esc_path:
            esc_auth = await self.session.get(Authority, esc_path.to_authority_id)
            if esc_auth:
                escalation_read = AuthorityRead.model_validate(esc_auth)

        # Build action plan steps
        action_steps = [
            f"Step 1: Confirm jurisdiction with {primary_auth.authority_name}.",
            "Step 2: Collect and organize all supporting evidentiary documents.",
        ]
        if procedure and procedure.complaint_method:
            action_steps.append(f"Step 3: Submit complaint via official method: {procedure.complaint_method}.")
        else:
            action_steps.append("Step 3: File formal petition before the registry.")

        if esc_path:
            action_steps.append(f"Step 4: If grievance is unaddressed or adverse order is passed, escalate to {esc_path.to_authority_id} ({esc_path.time_limit}).")

        # Applicable laws summary
        applicable_central = []
        if category == "consumer_dispute":
            applicable_central.append("Consumer Protection Act, 2019")
            applicable_central.append("Consumer Protection (Consumer Commission Procedure) Regulations, 2020")
        elif category == "real_estate":
            applicable_central.append("Real Estate (Regulation and Development) Act, 2016 (RERA)")
        elif category == "legal_aid":
            applicable_central.append("Constitution of India, Article 39A (Free Legal Aid)")
            applicable_central.append("Legal Services Authorities Act, 1987")
        elif category == "human_rights":
            applicable_central.append("Protection of Human Rights Act, 1993")

        return AuthorityRoutingResult(
            jurisdiction_analysis=JurisdictionAnalysis(
                is_determined=True,
                jurisdiction_type=primary_auth.authority_level,
                reasoning=f"Jurisdiction determined under {primary_auth.authority_level.value.upper()} level authority ({primary_auth.authority_name}) for {district.district_name}, {state.state_name}."
            ),
            primary_authority=primary_read,
            escalation_authority=escalation_read,
            complaint_procedure=procedure,
            applicable_central_laws=applicable_central,
            applicable_state_laws=[],
            action_plan_steps=action_steps,
        )
