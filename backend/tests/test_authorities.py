"""
Automated tests for State, District, and Authority routing architecture.

Tests:
1. States exist (Telangana, Andhra Pradesh, Maharashtra, Delhi)
2. Districts correctly belong to states (33 for TS, 26 for AP, 36 for MH, 11 for DL)
3. No duplicate districts within a state
4. Authority State/District relationships are valid
5. Unverified authority records are never presented as VERIFIED
6. Official source metadata is preserved
7. Routing does not return an authority outside its jurisdiction
8. API endpoints function correctly with proper validation and error handling
"""

import pytest
import pytest_asyncio
import sys
from pathlib import Path
from httpx import AsyncClient, ASGITransport

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.core.database import AsyncSessionLocal, create_tables
from app.services.authority_seeder import seed_authorities_database
from app.services.authority_routing_service import AuthorityRoutingService
from app.models.authority import (
    State,
    District,
    Authority,
    AuthorityLevel,
    VerificationStatusDB,
    SourceTypeDB,
)


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_db():
    """Ensure tables exist and are seeded before running tests."""
    await create_tables()
    await seed_authorities_database()


@pytest.mark.asyncio
async def test_states_exist():
    async with AsyncSessionLocal() as session:
        service = AuthorityRoutingService(session)
        states = await service.get_states()
        state_ids = [s.state_id for s in states]

        assert len(states) == 4, f"Expected 4 states, got {len(states)}"
        assert "TS" in state_ids, "Telangana missing"
        assert "AP" in state_ids, "Andhra Pradesh missing"
        assert "MH" in state_ids, "Maharashtra missing"
        assert "DL" in state_ids, "Delhi missing"

        # Check Delhi is union territory
        dl = await service.get_state("DL")
        assert dl is not None
        assert dl.is_union_territory is True
        assert dl.state_type == "union_territory"

        # Check Telangana is state
        ts = await service.get_state("TS")
        assert ts is not None
        assert ts.is_union_territory is False
        assert ts.state_type == "state"


@pytest.mark.asyncio
async def test_districts_belong_to_states():
    async with AsyncSessionLocal() as session:
        service = AuthorityRoutingService(session)

        # Telangana: 33 official districts
        ts_districts = await service.get_districts_by_state("TS")
        assert len(ts_districts) == 33, f"Expected 33 districts for TS, got {len(ts_districts)}"
        for d in ts_districts:
            assert d.state_id == "TS"

        # Andhra Pradesh: 26 official districts
        ap_districts = await service.get_districts_by_state("AP")
        assert len(ap_districts) == 26, f"Expected 26 districts for AP, got {len(ap_districts)}"
        for d in ap_districts:
            assert d.state_id == "AP"

        # Maharashtra: 36 official districts
        mh_districts = await service.get_districts_by_state("MH")
        assert len(mh_districts) == 36, f"Expected 36 districts for MH, got {len(mh_districts)}"
        for d in mh_districts:
            assert d.state_id == "MH"

        # Delhi: 11 official revenue districts
        dl_districts = await service.get_districts_by_state("DL")
        assert len(dl_districts) == 11, f"Expected 11 districts for DL, got {len(dl_districts)}"
        for d in dl_districts:
            assert d.state_id == "DL"


@pytest.mark.asyncio
async def test_no_duplicate_districts_within_state():
    async with AsyncSessionLocal() as session:
        service = AuthorityRoutingService(session)

        for state_code in ["TS", "AP", "MH", "DL"]:
            districts = await service.get_districts_by_state(state_code)
            names = [d.district_name.lower().strip() for d in districts]
            ids = [d.district_id for d in districts]

            assert len(names) == len(set(names)), f"Duplicate district names found in {state_code}: {names}"
            assert len(ids) == len(set(ids)), f"Duplicate district IDs found in {state_code}: {ids}"


@pytest.mark.asyncio
async def test_authority_state_district_relationships():
    async with AsyncSessionLocal() as session:
        service = AuthorityRoutingService(session)
        authorities = await service.get_authorities()

        assert len(authorities) >= 9, f"Expected at least 9 authorities, got {len(authorities)}"

        for auth in authorities:
            # If district_id is set, state_id must also be set
            if auth.district_id:
                assert auth.state_id is not None, f"District authority {auth.authority_id} has no state_id"
                district = await service.get_district(auth.district_id)
                assert district is not None, f"District {auth.district_id} does not exist for {auth.authority_id}"
                assert district.state_id == auth.state_id, (
                    f"District {auth.district_id} belongs to {district.state_id}, not {auth.state_id}"
                )

            # If state_id is set, it must exist in states table
            if auth.state_id:
                state = await service.get_state(auth.state_id)
                assert state is not None, f"State {auth.state_id} does not exist for {auth.authority_id}"

            # Central authority must not have state_id
            if auth.authority_level == AuthorityLevel.CENTRAL:
                assert auth.state_id is None, f"Central authority {auth.authority_id} must have state_id=None"
                assert auth.district_id is None, f"Central authority {auth.authority_id} must have district_id=None"


@pytest.mark.asyncio
async def test_unverified_records_not_presented_as_verified():
    async with AsyncSessionLocal() as session:
        service = AuthorityRoutingService(session)
        authorities = await service.get_authorities()

        for auth in authorities:
            # Rule: only official/court sources can have verification_status=verified
            if auth.verification_status == VerificationStatusDB.VERIFIED:
                assert auth.source_type in [SourceTypeDB.OFFICIAL, SourceTypeDB.COURT], (
                    f"Authority {auth.authority_id} is marked VERIFIED but has source_type {auth.source_type}"
                )
                assert auth.source_url is not None and auth.source_url.startswith("http"), (
                    f"Verified authority {auth.authority_id} has no valid source_url"
                )
                assert "indiankanoon" not in auth.source_url.lower(), (
                    f"IndianKanoon is labeled as verified authority source in {auth.authority_id}"
                )


@pytest.mark.asyncio
async def test_official_source_metadata_preserved():
    async with AsyncSessionLocal() as session:
        service = AuthorityRoutingService(session)
        authorities = await service.get_authorities()

        for auth in authorities:
            assert auth.source_url, f"Missing source_url in {auth.authority_id}"
            assert auth.source_type, f"Missing source_type in {auth.authority_id}"
            assert auth.source_authority, f"Missing source_authority in {auth.authority_id}"
            assert auth.last_verified, f"Missing last_verified in {auth.authority_id}"

            # No dummy emails or dummy phone numbers
            if auth.official_email:
                assert "@" in auth.official_email and "example.com" not in auth.official_email
            if auth.official_phone:
                assert "12345" not in auth.official_phone


@pytest.mark.asyncio
async def test_routing_jurisdiction_bounds():
    async with AsyncSessionLocal() as session:
        service = AuthorityRoutingService(session)

        # Query Telangana consumer dispute
        res_ts = await service.route_action_query(
            state_id="TS",
            district_id="TS-HYD",
            legal_category="consumer_dispute"
        )
        assert res_ts.jurisdiction_analysis.is_determined is True
        assert res_ts.primary_authority is not None
        assert res_ts.primary_authority.authority_id == "TS-DCDRC-HYD"
        assert res_ts.primary_authority.state_id == "TS"
        # Escalation must be Telangana State Commission
        assert res_ts.escalation_authority is not None
        assert res_ts.escalation_authority.authority_id == "TS-SCDRC"

        # Query Maharashtra real estate dispute
        res_mh = await service.route_action_query(
            state_id="MH",
            district_id="MH-MUMC",  # Mumbai City
            legal_category="real_estate"
        )
        assert res_mh.jurisdiction_analysis.is_determined is True
        assert res_mh.primary_authority is not None
        assert res_mh.primary_authority.authority_id == "MH-MAHARERA"
        assert res_mh.primary_authority.state_id == "MH"

        # Query Nationwide Human Rights
        res_hr = await service.route_action_query(
            state_id="DL",
            district_id="DL-NEW",
            legal_category="human_rights"
        )
        assert res_hr.jurisdiction_analysis.is_determined is True
        assert res_hr.primary_authority is not None
        assert res_hr.primary_authority.authority_id == "IN-NHRC"
        assert res_hr.primary_authority.authority_level == AuthorityLevel.CENTRAL

        # Query with missing category -> system must report undetermined and request info
        res_missing = await service.route_action_query(
            state_id="TS",
            district_id="TS-HYD",
            legal_category=None
        )
        assert res_missing.jurisdiction_analysis.is_determined is False
        assert res_missing.jurisdiction_analysis.missing_information is not None
        assert "category" in res_missing.jurisdiction_analysis.missing_information.lower()

        # Query with invalid state
        res_invalid_state = await service.route_action_query(
            state_id="XX",
            district_id="XX-FAKE",
            legal_category="consumer_dispute"
        )
        assert res_invalid_state.jurisdiction_analysis.is_determined is False


@pytest.mark.asyncio
async def test_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. GET /states
        r = await client.get("/states")
        assert r.status_code == 200
        states = r.json()
        assert len(states) == 4

        # 2. GET /states/TS/districts
        r = await client.get("/states/TS/districts")
        assert r.status_code == 200
        districts = r.json()
        assert len(districts) == 33

        # 3. GET /authorities with filters
        r = await client.get("/authorities?state_id=TS&district_id=TS-HYD")
        assert r.status_code == 200
        auths = r.json()
        auth_ids = [a["authority_id"] for a in auths]
        assert "TS-DCDRC-HYD" in auth_ids
        assert "TS-SCDRC" in auth_ids
        assert "IN-NCDRC" in auth_ids  # Central authority also covers it
        assert "MH-MAHARERA" not in auth_ids  # Out-of-state authority must NOT be returned

        # 4. GET /authorities/{id} detail
        r = await client.get("/authorities/TS-DCDRC-HYD")
        assert r.status_code == 200
        detail = r.json()
        assert detail["authority"]["authority_id"] == "TS-DCDRC-HYD"
        assert len(detail["complaint_procedures"]) >= 1
        assert len(detail["escalation_paths"]) >= 1

        # 5. GET /route (Action Mode)
        r = await client.get("/route?state_id=TS&district_id=TS-HYD&legal_category=consumer_dispute")
        assert r.status_code == 200
        route_res = r.json()
        assert route_res["jurisdiction_analysis"]["is_determined"] is True
        assert route_res["primary_authority"]["authority_id"] == "TS-DCDRC-HYD"
        assert route_res["escalation_authority"]["authority_id"] == "TS-SCDRC"
        assert len(route_res["action_plan_steps"]) >= 3


if __name__ == "__main__":
    import asyncio
    print("Running authority and routing tests directly...")
    asyncio.run(setup_db())
    asyncio.run(test_states_exist())
    print("[PASS] test_states_exist passed")
    asyncio.run(test_districts_belong_to_states())
    print("[PASS] test_districts_belong_to_states passed")
    asyncio.run(test_no_duplicate_districts_within_state())
    print("[PASS] test_no_duplicate_districts_within_state passed")
    asyncio.run(test_authority_state_district_relationships())
    print("[PASS] test_authority_state_district_relationships passed")
    asyncio.run(test_unverified_records_not_presented_as_verified())
    print("[PASS] test_unverified_records_not_presented_as_verified passed")
    asyncio.run(test_official_source_metadata_preserved())
    print("[PASS] test_official_source_metadata_preserved passed")
    asyncio.run(test_routing_jurisdiction_bounds())
    print("[PASS] test_routing_jurisdiction_bounds passed")
    asyncio.run(test_api_endpoints())
    print("[PASS] test_api_endpoints passed")
    print("\nALL 8 AUTHORITY TESTS PASSED!")
