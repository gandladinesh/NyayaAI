"""
Database seeder service for States, Districts, Authorities,
Complaint Procedures, and Escalation Paths.
"""

import json
from datetime import date, datetime
from pathlib import Path
import sys

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import AsyncSessionLocal, create_tables
from app.models.authority import (
    State,
    District,
    Authority,
    AuthorityJurisdiction,
    ComplaintProcedure,
    EscalationPath,
    AuthorityType,
    AuthorityLevel,
    SourceTypeDB,
    VerificationStatusDB,
)

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "seed_authorities.json"


def parse_date(d_str: str) -> date:
    if isinstance(d_str, date):
        return d_str
    return datetime.strptime(d_str, "%Y-%m-%d").date()


async def seed_authorities_database() -> dict:
    """Idempotently seed states, districts, and authority records into DB."""
    await create_tables()

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Seed authorities file not found at {DATA_PATH}")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    stats = {
        "states_added": 0,
        "districts_added": 0,
        "authorities_added": 0,
        "jurisdictions_added": 0,
        "procedures_added": 0,
        "escalation_paths_added": 0,
    }

    async with AsyncSessionLocal() as session:
        # 1. Seed States
        for s_data in data.get("states", []):
            existing = await session.get(State, s_data["state_id"])
            if not existing:
                state_obj = State(
                    state_id=s_data["state_id"],
                    state_name=s_data["state_name"],
                    state_code=s_data["state_code"],
                    state_type=s_data.get("state_type", "state"),
                    capital=s_data.get("capital"),
                    high_court=s_data.get("high_court"),
                    high_court_url=s_data.get("high_court_url"),
                    is_union_territory=s_data.get("is_union_territory", False),
                    status=s_data.get("status", "active"),
                    source_url=s_data["source_url"],
                    last_verified=parse_date(s_data["last_verified"]),
                )
                session.add(state_obj)
                stats["states_added"] += 1

        await session.commit()

        # 2. Seed Districts
        for d_data in data.get("districts", []):
            existing = await session.get(District, d_data["district_id"])
            if not existing:
                district_obj = District(
                    district_id=d_data["district_id"],
                    state_id=d_data["state_id"],
                    district_name=d_data["district_name"],
                    district_code=d_data.get("district_code"),
                    headquarters=d_data.get("headquarters"),
                    status=d_data.get("status", "active"),
                    source_url=d_data["source_url"],
                    last_verified=parse_date(d_data["last_verified"]),
                )
                session.add(district_obj)
                stats["districts_added"] += 1

        await session.commit()

        # 3. Seed Authorities
        for a_data in data.get("authorities", []):
            existing = await session.get(Authority, a_data["authority_id"])
            if not existing:
                auth_obj = Authority(
                    authority_id=a_data["authority_id"],
                    authority_name=a_data["authority_name"],
                    authority_type=AuthorityType(a_data["authority_type"]),
                    authority_level=AuthorityLevel(a_data["authority_level"]),
                    state_id=a_data.get("state_id"),
                    district_id=a_data.get("district_id"),
                    jurisdiction_desc=a_data.get("jurisdiction_desc"),
                    official_address=a_data.get("official_address"),
                    official_website=a_data.get("official_website"),
                    official_email=a_data.get("official_email"),
                    official_phone=a_data.get("official_phone"),
                    complaint_url=a_data.get("complaint_url"),
                    source_url=a_data["source_url"],
                    source_type=SourceTypeDB(a_data["source_type"]),
                    source_authority=a_data["source_authority"],
                    verification_status=VerificationStatusDB(a_data.get("verification_status", "verified")),
                    last_verified=parse_date(a_data["last_verified"]),
                    is_active=a_data.get("is_active", True),
                )
                session.add(auth_obj)
                stats["authorities_added"] += 1

        await session.commit()

        # 4. Seed Authority Jurisdictions
        for j_data in data.get("authority_jurisdictions", []):
            stmt = select(AuthorityJurisdiction).where(
                AuthorityJurisdiction.authority_id == j_data["authority_id"],
                AuthorityJurisdiction.legal_category == j_data["legal_category"],
            )
            res = await session.execute(stmt)
            if not res.scalars().first():
                j_obj = AuthorityJurisdiction(
                    authority_id=j_data["authority_id"],
                    legal_category=j_data["legal_category"],
                    jurisdiction_notes=j_data.get("jurisdiction_notes"),
                )
                session.add(j_obj)
                stats["jurisdictions_added"] += 1

        await session.commit()

        # 5. Seed Complaint Procedures
        for p_data in data.get("complaint_procedures", []):
            existing = await session.get(ComplaintProcedure, p_data["procedure_id"])
            if not existing:
                proc_obj = ComplaintProcedure(
                    procedure_id=p_data["procedure_id"],
                    authority_id=p_data["authority_id"],
                    legal_category=p_data.get("legal_category"),
                    complaint_method=p_data.get("complaint_method"),
                    procedure_steps_json=p_data.get("procedure_steps_json"),
                    time_limit=p_data.get("time_limit"),
                    fee=p_data.get("fee"),
                    format_required=p_data.get("format_required"),
                    required_docs_json=p_data.get("required_docs_json"),
                    escalation_authority_id=p_data.get("escalation_authority_id"),
                    source_url=p_data["source_url"],
                    source_type=SourceTypeDB(p_data["source_type"]),
                    verification_status=VerificationStatusDB(p_data.get("verification_status", "verified")),
                    last_verified=parse_date(p_data["last_verified"]),
                )
                session.add(proc_obj)
                stats["procedures_added"] += 1

        await session.commit()

        # 6. Seed Escalation Paths
        for e_data in data.get("escalation_paths", []):
            stmt = select(EscalationPath).where(
                EscalationPath.from_authority_id == e_data["from_authority_id"],
                EscalationPath.to_authority_id == e_data["to_authority_id"],
                EscalationPath.legal_category == e_data.get("legal_category"),
            )
            res = await session.execute(stmt)
            if not res.scalars().first():
                esc_obj = EscalationPath(
                    from_authority_id=e_data["from_authority_id"],
                    to_authority_id=e_data["to_authority_id"],
                    legal_category=e_data.get("legal_category"),
                    escalation_trigger=e_data.get("escalation_trigger"),
                    time_limit=e_data.get("time_limit"),
                    source_url=e_data["source_url"],
                    last_verified=parse_date(e_data["last_verified"]),
                )
                session.add(esc_obj)
                stats["escalation_paths_added"] += 1

        await session.commit()

    return stats


if __name__ == "__main__":
    import asyncio
    res = asyncio.run(seed_authorities_database())
    print("Database seeding completed:", res)
