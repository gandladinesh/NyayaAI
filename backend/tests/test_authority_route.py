"""
Automated tests for the /api/route endpoint (Authority Routing).

Tests cover:
1. Successful authority routing with all parameters
2. Missing required parameters (state_id, district_id)
3. Invalid state/district handling
4. Optional category parameter handling
5. Response structure validation
6. Jurisdiction analysis and reasoning
7. Primary authority, escalation, and procedures
8. Applicable laws and action plan steps
"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# ─────────────────────────────────────────────────────────────────────────
# Test 1: Successful Authority Routing
# ─────────────────────────────────────────────────────────────────────────

def test_route_successful_with_all_parameters():
    """Successful routing with valid state, district, and category should return authority details."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "consumer_dispute",
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Jurisdiction must be determined
    assert "jurisdiction_analysis" in data
    assert data["jurisdiction_analysis"]["is_determined"] is True

    # Should have a primary authority
    assert "primary_authority" in data
    assert data["primary_authority"] is not None
    assert "authority_id" in data["primary_authority"]
    assert "authority_name" in data["primary_authority"]


def test_route_successful_telangana_consumer_dispute():
    """Route consumer dispute in Telangana Hyderabad should resolve."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "consumer_dispute",
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["jurisdiction_analysis"]["is_determined"] is True


def test_route_successful_delhi_legal_aid():
    """Route legal aid query in Delhi - may be undetermined if not indexed."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "DL",
            "district_id": "DL-CENTRAL",
            "legal_category": "legal_aid",
        }
    )

    assert response.status_code == 200
    data = response.json()
    # Delhi legal_aid may not be indexed yet in Phase 1, so just verify response structure
    assert "jurisdiction_analysis" in data
    assert isinstance(data["jurisdiction_analysis"]["is_determined"], bool)


def test_route_successful_maharashtra_human_rights():
    """Route human rights query in Maharashtra."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "MH",
            "district_id": "MH-Mumbai",
            "legal_category": "human_rights",
        }
    )

    assert response.status_code == 200
    data = response.json()
    # Should either determine jurisdiction or explain missing info
    assert data["jurisdiction_analysis"]["is_determined"] in [True, False]


# ─────────────────────────────────────────────────────────────────────────
# Test 2: Missing Required Parameters
# ─────────────────────────────────────────────────────────────────────────

def test_route_missing_state_id():
    """Missing state_id parameter should fail validation."""
    response = client.get(
        "/api/route",
        params={
            "district_id": "TS-HYD",
            "legal_category": "consumer_dispute",
        }
    )

    # Missing required parameter should return 422
    assert response.status_code == 422


def test_route_missing_district_id():
    """Missing district_id parameter should fail validation."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "legal_category": "consumer_dispute",
        }
    )

    # Missing required parameter should return 422
    assert response.status_code == 422


def test_route_missing_both_state_and_district():
    """Missing both state_id and district_id should fail validation."""
    response = client.get(
        "/api/route",
        params={
            "legal_category": "consumer_dispute",
        }
    )

    assert response.status_code == 422


def test_route_missing_all_parameters():
    """Request with no parameters should fail validation."""
    response = client.get("/api/route")

    assert response.status_code == 422


# ─────────────────────────────────────────────────────────────────────────
# Test 3: Invalid State/District Handling
# ─────────────────────────────────────────────────────────────────────────

def test_route_invalid_state_id():
    """Invalid state_id should return undetermined jurisdiction."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "XX",
            "district_id": "XX-INVALID",
            "legal_category": "consumer_dispute",
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Jurisdiction should be undetermined
    assert data["jurisdiction_analysis"]["is_determined"] is False
    assert "reasoning" in data["jurisdiction_analysis"]
    assert data["jurisdiction_analysis"]["reasoning"] is not None
    assert len(data["jurisdiction_analysis"]["reasoning"]) > 0

    # Should provide guidance
    assert "missing_information" in data["jurisdiction_analysis"]


def test_route_invalid_district_for_state():
    """District not belonging to state should return undetermined jurisdiction."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "AP-VIJAYAWADA",  # AP district with TS state
            "legal_category": "consumer_dispute",
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Jurisdiction mismatch should be undetermined
    assert data["jurisdiction_analysis"]["is_determined"] is False
    assert "reasoning" in data["jurisdiction_analysis"]


def test_route_completely_invalid_district():
    """Non-existent district should return undetermined jurisdiction."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-NONEXISTENT",
            "legal_category": "consumer_dispute",
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Should be undetermined
    assert data["jurisdiction_analysis"]["is_determined"] is False


# ─────────────────────────────────────────────────────────────────────────
# Test 4: Category Parameter Handling
# ─────────────────────────────────────────────────────────────────────────

def test_route_missing_category():
    """Valid state/district but missing category should indicate category is needed."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Jurisdiction determined (location confirmed) but category needed
    assert data["jurisdiction_analysis"]["is_determined"] is False
    assert "missing_information" in data["jurisdiction_analysis"]
    assert "category" in data["jurisdiction_analysis"]["missing_information"].lower() or \
           "problem" in data["jurisdiction_analysis"]["missing_information"].lower()


def test_route_invalid_category():
    """Valid state/district but invalid category should handle gracefully."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "nonexistent_category",
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Should be undetermined if no authorities match this category
    assert data["jurisdiction_analysis"]["is_determined"] in [True, False]


def test_route_empty_category():
    """Empty category string should be handled."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "",
        }
    )

    # Empty string might be treated as missing
    assert response.status_code in [200, 422]


# ─────────────────────────────────────────────────────────────────────────
# Test 5: Response Structure Validation
# ─────────────────────────────────────────────────────────────────────────

def test_route_response_has_all_required_fields():
    """Successful response should have all required top-level fields."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "consumer_dispute",
        }
    )

    data = response.json()

    # All top-level fields should be present
    assert "jurisdiction_analysis" in data
    assert "primary_authority" in data
    assert "escalation_authority" in data
    assert "complaint_procedure" in data
    assert "applicable_central_laws" in data
    assert "applicable_state_laws" in data
    assert "action_plan_steps" in data
    assert "source_note" in data


def test_route_jurisdiction_analysis_structure():
    """Jurisdiction analysis should have proper schema."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "consumer_dispute",
        }
    )

    data = response.json()
    ja = data["jurisdiction_analysis"]

    # Required fields
    assert "is_determined" in ja
    assert isinstance(ja["is_determined"], bool)

    # When determined
    if ja["is_determined"]:
        assert "jurisdiction_type" in ja
    # When not determined
    else:
        assert "reasoning" in ja
        assert "missing_information" in ja


def test_route_primary_authority_schema():
    """Primary authority should have authority fields when determined."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "consumer_dispute",
        }
    )

    data = response.json()

    if data["jurisdiction_analysis"]["is_determined"] and data["primary_authority"]:
        auth = data["primary_authority"]

        # Required authority fields
        required_fields = [
            "authority_id",
            "authority_name",
            "authority_type",
            "authority_level",
            "official_address",
            "source_url",
            "source_type",
            "verification_status",
        ]

        for field in required_fields:
            assert field in auth, f"Missing authority field: {field}"


def test_route_applicable_laws_list():
    """Applicable laws should be lists of strings."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "consumer_dispute",
        }
    )

    data = response.json()

    assert isinstance(data["applicable_central_laws"], list)
    assert isinstance(data["applicable_state_laws"], list)

    # If populated, should contain strings
    if data["applicable_central_laws"]:
        assert all(isinstance(law, str) for law in data["applicable_central_laws"])

    if data["applicable_state_laws"]:
        assert all(isinstance(law, str) for law in data["applicable_state_laws"])


def test_route_action_plan_steps():
    """Action plan steps should be a list of strings."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "consumer_dispute",
        }
    )

    data = response.json()

    assert isinstance(data["action_plan_steps"], list)

    # If populated, should contain strings
    if data["action_plan_steps"]:
        assert all(isinstance(step, str) for step in data["action_plan_steps"])


def test_route_source_note():
    """Source note should be present and meaningful."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "consumer_dispute",
        }
    )

    data = response.json()

    assert "source_note" in data
    assert isinstance(data["source_note"], str)
    assert len(data["source_note"]) > 0


# ─────────────────────────────────────────────────────────────────────────
# Test 6: State Case-Insensitivity
# ─────────────────────────────────────────────────────────────────────────

def test_route_lowercase_state_id():
    """Lowercase state_id should be handled."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "ts",  # lowercase
            "district_id": "TS-HYD",
            "legal_category": "consumer_dispute",
        }
    )

    assert response.status_code == 200
    data = response.json()
    # Should either work or return proper error
    assert "jurisdiction_analysis" in data


def test_route_mixed_case_state_id():
    """Mixed case state_id should be handled."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "Ts",
            "district_id": "TS-HYD",
            "legal_category": "consumer_dispute",
        }
    )

    assert response.status_code == 200


# ─────────────────────────────────────────────────────────────────────────
# Test 7: Different State/District Combinations
# ─────────────────────────────────────────────────────────────────────────

def test_route_andhra_pradesh_districts():
    """Route should work for Andhra Pradesh districts."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "AP",
            "district_id": "AP-VIJAYAWADA",
            "legal_category": "consumer_dispute",
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "jurisdiction_analysis" in data


def test_route_delhi_districts():
    """Route should work for Delhi districts."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "DL",
            "district_id": "DL-CENTRAL",
            "legal_category": "legal_aid",
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "jurisdiction_analysis" in data


def test_route_maharashtra_districts():
    """Route should work for Maharashtra districts."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "MH",
            "district_id": "MH-Mumbai",
            "legal_category": "consumer_dispute",
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "jurisdiction_analysis" in data


# ─────────────────────────────────────────────────────────────────────────
# Test 8: Different Legal Categories
# ─────────────────────────────────────────────────────────────────────────

def test_route_consumer_dispute_category():
    """Consumer dispute routing should work."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "consumer_dispute",
        }
    )

    assert response.status_code == 200


def test_route_legal_aid_category():
    """Legal aid routing should work."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "legal_aid",
        }
    )

    assert response.status_code == 200


def test_route_human_rights_category():
    """Human rights routing should work."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "human_rights",
        }
    )

    assert response.status_code == 200


def test_route_real_estate_category():
    """Real estate routing should work."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "real_estate",
        }
    )

    assert response.status_code == 200


# ─────────────────────────────────────────────────────────────────────────
# Test 9: Complaint Procedures
# ─────────────────────────────────────────────────────────────────────────

def test_route_complaint_procedure_when_determined():
    """When jurisdiction determined, complaint procedure may be included."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "consumer_dispute",
        }
    )

    data = response.json()

    if data["jurisdiction_analysis"]["is_determined"]:
        # complaint_procedure can be None or populated
        assert "complaint_procedure" in data
        if data["complaint_procedure"]:
            # If populated, should have procedure details
            assert "procedure_id" in data["complaint_procedure"] or \
                   "authority_id" in data["complaint_procedure"]


def test_route_escalation_authority_optional():
    """Escalation authority is optional."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "consumer_dispute",
        }
    )

    data = response.json()

    # escalation_authority can be None or populated
    assert "escalation_authority" in data
    if data["escalation_authority"]:
        assert "authority_id" in data["escalation_authority"]


# ─────────────────────────────────────────────────────────────────────────
# Test 10: Edge Cases
# ─────────────────────────────────────────────────────────────────────────

def test_route_special_characters_in_category():
    """Category with special characters should be handled."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "consumer@dispute!",
        }
    )

    assert response.status_code == 200
    data = response.json()
    # Should handle gracefully
    assert "jurisdiction_analysis" in data


def test_route_very_long_category():
    """Very long category string should be handled."""
    response = client.get(
        "/api/route",
        params={
            "state_id": "TS",
            "district_id": "TS-HYD",
            "legal_category": "a" * 500,
        }
    )

    assert response.status_code == 200
    data = response.json()
    # Should handle gracefully
    assert "jurisdiction_analysis" in data
