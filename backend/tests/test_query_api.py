"""
Automated tests for the /api/query endpoint.

Tests cover:
1. Successful query with relevant provisions
2. No relevant provision response
3. Empty/invalid question handling
4. Question length boundary validation
5. top_k parameter boundary/validation
6. Response structure and schema validation
"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# ─────────────────────────────────────────────────────────────────────────
# Test 1: Successful Query with Relevant Provision
# ─────────────────────────────────────────────────────────────────────────

def test_query_success_right_to_life():
    """Query for a well-covered legal concept (Right to Life) should return success."""
    response = client.post(
        "/api/query",
        json={"question": "What is the right to life?", "top_k": 3},
    )

    assert response.status_code == 200
    data = response.json()

    # Response status should be "success"
    assert data["status"] == "success"
    assert "question" in data
    assert data["question"] == "What is the right to life?"

    # Should have a primary result
    assert data["primary_result"] is not None
    assert isinstance(data["primary_result"], dict)

    # Should have exact_text and AI explanation
    assert "exact_text" in data["primary_result"]
    assert "ai_explanation" in data["primary_result"]
    assert len(data["primary_result"]["exact_text"]) > 0
    assert len(data["primary_result"]["ai_explanation"]) > 0

    # Should have basic provision metadata
    assert "provision_id" in data["primary_result"]
    assert "reference_number" in data["primary_result"]
    assert "act" in data["primary_result"]
    assert "source_type" in data["primary_result"]
    assert "verification_status" in data["primary_result"]

    # Related results should be a list
    assert isinstance(data["related_results"], list)


def test_query_success_equality_before_law():
    """Query about equality should return Article 14 or related provisions."""
    response = client.post(
        "/api/query",
        json={"question": "What is equality before law?"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert data["primary_result"] is not None
    assert "exact_text" in data["primary_result"]
    assert len(data["primary_result"]["exact_text"]) > 0


def test_query_response_structure_includes_case_authorities():
    """Successful query should include case_authorities in primary_result."""
    response = client.post(
        "/api/query",
        json={"question": "What is the right to life?", "top_k": 3},
    )

    data = response.json()

    # primary_result should have case_authorities field
    assert "case_authorities" in data["primary_result"]
    assert isinstance(data["primary_result"]["case_authorities"], list)

    # Each case authority should have required fields
    for authority in data["primary_result"]["case_authorities"]:
        assert "case_id" in authority
        assert "case_name" in authority
        assert "citation" in authority
        assert "court" in authority
        assert "legal_principle" in authority
        assert "verification_status" in authority


def test_query_includes_related_results():
    """Successful query should return related_results when top_k > 1."""
    response = client.post(
        "/api/query",
        json={"question": "What is fundamental rights?", "top_k": 3},
    )

    data = response.json()

    # With top_k=3, we should have 2 related results (1 primary + 2 related)
    assert data["status"] == "success"
    related = data["related_results"]
    assert isinstance(related, list)
    # Should have some related results (exact number depends on corpus matches)
    if len(related) > 0:
        # Each related result should follow the same structure as primary
        assert "provision_id" in related[0]
        assert "exact_text" in related[0]
        assert "ai_explanation" in related[0]


# ─────────────────────────────────────────────────────────────────────────
# Test 2: No Relevant Provision Response
# ─────────────────────────────────────────────────────────────────────────

def test_query_no_relevant_provision():
    """Query with nonsensical terms should return no_relevant_provision status."""
    response = client.post(
        "/api/query",
        json={"question": "xyzabc fghijklmnop qrstuv"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "no_relevant_provision"
    assert data["message"] is not None
    assert "could not find" in data["message"].lower()
    assert data["primary_result"] is None
    assert data["related_results"] == []


def test_query_nonsense_question():
    """Query with random characters should not crash and return appropriate response."""
    response = client.post(
        "/api/query",
        json={"question": "kfhsdkfhskdfhskdhfskdhf"},
    )

    assert response.status_code == 200
    data = response.json()
    # Should be either no_relevant_provision or handle gracefully
    assert data["status"] in ["no_relevant_provision", "invalid"]


# ─────────────────────────────────────────────────────────────────────────
# Test 3: Empty/Invalid Question Handling
# ─────────────────────────────────────────────────────────────────────────

def test_query_empty_question_string():
    """Query with empty string should return invalid status."""
    response = client.post(
        "/api/query",
        json={"question": ""},
    )

    # Empty string fails Pydantic validation (min_length=1)
    assert response.status_code == 422


def test_query_whitespace_only_question():
    """Query with only whitespace should be treated as invalid."""
    response = client.post(
        "/api/query",
        json={"question": "   "},
    )

    # Whitespace-only should either fail validation or be stripped to invalid
    # The QueryRequest has min_length=1, but "   " passes that validation
    # The service strips it, so it becomes empty
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "invalid"
    assert data["primary_result"] is None


def test_query_missing_question_field():
    """Query without question field should fail validation."""
    response = client.post(
        "/api/query",
        json={"top_k": 3},
    )

    assert response.status_code == 422  # Validation error


# ─────────────────────────────────────────────────────────────────────────
# Test 4: Question Length Boundary Validation
# ─────────────────────────────────────────────────────────────────────────

def test_query_min_length_one_character():
    """Question with exactly 1 character should be accepted."""
    response = client.post(
        "/api/query",
        json={"question": "a"},
    )

    assert response.status_code == 200
    # May or may not find relevant provision, but request should be accepted
    data = response.json()
    assert data["status"] in ["success", "no_relevant_provision", "invalid"]


def test_query_max_length_2000_characters():
    """Question with exactly 2000 characters should be accepted."""
    long_question = "a" * 2000
    response = client.post(
        "/api/query",
        json={"question": long_question},
    )

    assert response.status_code == 200
    data = response.json()
    # Should be accepted, may or may not find results
    assert data["status"] in ["success", "no_relevant_provision", "invalid"]


def test_query_exceeds_max_length_2001_characters():
    """Question exceeding 2000 characters should fail validation."""
    long_question = "a" * 2001
    response = client.post(
        "/api/query",
        json={"question": long_question},
    )

    # Should fail Pydantic validation (max_length=2000)
    assert response.status_code == 422


def test_query_realistic_long_question():
    """Realistic long question within bounds should work."""
    long_question = (
        "What are my legal rights when a consumer product is defective "
        "and the seller refuses to provide a refund or replacement? "
        "Does the Consumer Protection Act apply in this situation? "
        "What remedies are available to me? Can I file a case in the "
        "District Consumer Disputes Redressal Commission or do I need "
        "to go to the State commission first?"
    )
    response = client.post(
        "/api/query",
        json={"question": long_question},
    )

    assert response.status_code == 200
    data = response.json()
    # Should be processed successfully
    assert data["status"] in ["success", "no_relevant_provision"]


# ─────────────────────────────────────────────────────────────────────────
# Test 5: top_k Parameter Boundary and Validation
# ─────────────────────────────────────────────────────────────────────────

def test_query_default_top_k():
    """Query without top_k should use default of 3."""
    response = client.post(
        "/api/query",
        json={"question": "What is a fundamental right?"},
    )

    assert response.status_code == 200
    data = response.json()
    # Top_k default is 3, so max 1 primary + 2 related
    if data["status"] == "success":
        assert len(data["related_results"]) <= 2


def test_query_top_k_minimum_1():
    """Query with top_k=1 should return only primary result."""
    response = client.post(
        "/api/query",
        json={"question": "What is the right to life?", "top_k": 1},
    )

    assert response.status_code == 200
    data = response.json()

    if data["status"] == "success":
        assert data["primary_result"] is not None
        assert len(data["related_results"]) == 0


def test_query_top_k_maximum_5():
    """Query with top_k=5 should be accepted."""
    response = client.post(
        "/api/query",
        json={"question": "What is a right?", "top_k": 5},
    )

    assert response.status_code == 200
    data = response.json()

    # Should be accepted, may return up to 4 related results
    if data["status"] == "success":
        assert len(data["related_results"]) <= 4


def test_query_top_k_below_minimum():
    """Query with top_k=0 should fail validation."""
    response = client.post(
        "/api/query",
        json={"question": "What is law?", "top_k": 0},
    )

    # Should fail Pydantic validation (ge=1)
    assert response.status_code == 422


def test_query_top_k_above_maximum():
    """Query with top_k=6 should fail validation."""
    response = client.post(
        "/api/query",
        json={"question": "What is law?", "top_k": 6},
    )

    # Should fail Pydantic validation (le=5)
    assert response.status_code == 422


def test_query_top_k_negative():
    """Query with negative top_k should fail validation."""
    response = client.post(
        "/api/query",
        json={"question": "What is law?", "top_k": -1},
    )

    assert response.status_code == 422


def test_query_top_k_non_integer():
    """Query with non-integer top_k should fail validation."""
    response = client.post(
        "/api/query",
        json={"question": "What is law?", "top_k": 3.5},
    )

    # FastAPI/Pydantic may coerce 3.5 to 3, or reject it
    # This is implementation-dependent, but should either work or fail validation
    assert response.status_code in [200, 422]


# ─────────────────────────────────────────────────────────────────────────
# Test 6: Response Structure Comprehensive Validation
# ─────────────────────────────────────────────────────────────────────────

def test_query_response_has_all_required_fields():
    """Response should always have all top-level fields."""
    response = client.post(
        "/api/query",
        json={"question": "What is equality?"},
    )

    assert response.status_code == 200
    data = response.json()

    # Top-level fields always present
    assert "status" in data
    assert "primary_result" in data
    assert "related_results" in data

    # "message" field is only present for non-success status
    if data["status"] != "success":
        assert "message" in data
    else:
        # Success responses have "question" instead of "message"
        assert "question" in data

    # Status must be one of the known values
    assert data["status"] in ["success", "no_relevant_provision", "invalid"]


def test_query_success_primary_result_schema():
    """Successful query's primary_result should have all required fields."""
    response = client.post(
        "/api/query",
        json={"question": "What is the right to life?"},
    )

    data = response.json()

    if data["status"] == "success":
        pr = data["primary_result"]

        # Required fields for provision
        required_fields = [
            "provision_id",
            "reference_number",
            "act",
            "exact_text",
            "ai_explanation",
            "official_citation",
            "source_name",
            "source_type",
            "verification_status",
            "source_url",
            "distance",
            "case_authorities",
        ]

        for field in required_fields:
            assert field in pr, f"Missing field: {field}"

        # Field types
        assert isinstance(pr["provision_id"], str)
        assert isinstance(pr["exact_text"], str)
        assert isinstance(pr["ai_explanation"], str)
        assert isinstance(pr["case_authorities"], list)
        assert isinstance(pr["distance"], (int, float))

        # Verification status should be one of known values
        assert pr["verification_status"] in [
            "VERIFIED",
            "PARTIALLY_VERIFIED",
            "UNVERIFIED",
            "verified",
            "partially_verified",
            "unverified",
        ]

        # Source type should be one of known values
        assert pr["source_type"] in [
            "official",
            "court",
            "supplementary",
            "OFFICIAL",
            "COURT",
            "SUPPLEMENTARY",
        ]


def test_query_case_authority_schema():
    """Each case authority should have required fields."""
    response = client.post(
        "/api/query",
        json={"question": "What is the right to life?"},
    )

    data = response.json()

    if data["status"] == "success" and data["primary_result"]["case_authorities"]:
        for auth in data["primary_result"]["case_authorities"]:
            required_fields = [
                "case_id",
                "case_name",
                "citation",
                "court",
                "judgment_date",
                "legal_principle",
                "source_name",
                "source_type",
                "source_url",
                "verification_status",
            ]

            for field in required_fields:
                assert field in auth, f"Missing case authority field: {field}"

            # Field types
            assert isinstance(auth["case_id"], str)
            assert isinstance(auth["case_name"], str)
            assert isinstance(auth["citation"], str)
            assert isinstance(auth["legal_principle"], str)


def test_query_no_provision_response_schema():
    """no_relevant_provision response should have proper schema."""
    response = client.post(
        "/api/query",
        json={"question": "xyzabc fghijklmnop"},
    )

    data = response.json()

    if data["status"] == "no_relevant_provision":
        assert data["primary_result"] is None
        assert data["related_results"] == []
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0


def test_query_invalid_response_schema():
    """invalid response should have proper schema."""
    response = client.post(
        "/api/query",
        json={"question": "   "},
    )

    data = response.json()

    if data["status"] == "invalid":
        assert data["primary_result"] is None
        assert data["related_results"] == []
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0


# ─────────────────────────────────────────────────────────────────────────
# Test 7: Category Parameter (Optional)
# ─────────────────────────────────────────────────────────────────────────

def test_query_with_category_filter():
    """Query with category filter should be accepted."""
    response = client.post(
        "/api/query",
        json={
            "question": "What is a right?",
            "category": "constitution",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["success", "no_relevant_provision", "invalid"]


def test_query_without_category_optional():
    """Query without category should work (it's optional)."""
    response = client.post(
        "/api/query",
        json={"question": "What is law?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "status" in data


# ─────────────────────────────────────────────────────────────────────────
# Additional Edge Cases
# ─────────────────────────────────────────────────────────────────────────

def test_query_special_characters():
    """Query with special characters should be handled safely."""
    response = client.post(
        "/api/query",
        json={"question": "What about §123 and Article 21 (a)?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["success", "no_relevant_provision", "invalid"]


def test_query_unicode_characters():
    """Query with Unicode characters should be handled."""
    response = client.post(
        "/api/query",
        json={"question": "क्या मेरे पास कानूनी अधिकार हैं?"},  # Hindi text
    )

    assert response.status_code == 200
    data = response.json()
    # Should handle unicode without crashing
    assert data["status"] in ["success", "no_relevant_provision", "invalid"]


def test_query_question_with_numbers():
    """Query with numerical values should be processed."""
    response = client.post(
        "/api/query",
        json={"question": "What is Article 15 of the Constitution?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["success", "no_relevant_provision"]
