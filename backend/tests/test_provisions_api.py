from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_all_provisions():
    response = client.get("/api/provisions")

    assert response.status_code == 200

    data = response.json()

    # Total corpus: 25 Constitution + 12 BNS + 8 BNSS + 5 BSA = 50
    assert data["count"] == 50
    assert len(data["provisions"]) == 50


def test_get_provisions_by_category():
    # Constitution filter
    res_const = client.get("/api/provisions", params={"category": "constitution"})
    assert res_const.status_code == 200
    assert res_const.json()["count"] == 25

    # BNS filter
    res_bns = client.get("/api/provisions", params={"category": "bns"})
    assert res_bns.status_code == 200
    assert res_bns.json()["count"] == 12

    # BNSS filter
    res_bnss = client.get("/api/provisions", params={"category": "bnss"})
    assert res_bnss.status_code == 200
    assert res_bnss.json()["count"] == 8

    # BSA filter
    res_bsa = client.get("/api/provisions", params={"category": "bsa"})
    assert res_bsa.status_code == 200
    assert res_bsa.json()["count"] == 5


def test_get_article_21_by_reference():
    response = client.get(
        "/api/provisions/reference/Article 21"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["provision_id"] == "constitution-india-article-21"
    assert data["reference_number"] == "Article 21"
    assert data["article_number"] == "21"


def test_search_privacy_finds_article_21():
    response = client.get(
        "/api/provisions",
        params={"search": "privacy"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert data["provisions"][0]["provision_id"] == (
        "constitution-india-article-21"
    )


def test_unknown_provision_returns_404():
    response = client.get(
        "/api/provisions/constitution-india-article-999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == (
        "Legal provision "
        "'constitution-india-article-999' not found."
    )


def test_get_bns_section_100_by_reference():
    response = client.get("/api/provisions/reference/Section 100")
    assert response.status_code == 200
    data = response.json()
    assert data["provision_id"] == "bns-2023-section-100"
    assert data["act_short"] == "BNS 2023"
    assert "murder" in data["short_title"].lower()


def test_get_bnss_section_173_by_reference():
    response = client.get("/api/provisions/reference/Section 173")
    assert response.status_code == 200
    data = response.json()
    assert data["provision_id"] == "bnss-2023-section-173"
    assert data["act_short"] == "BNSS 2023"


def test_get_bsa_section_65_by_reference():
    response = client.get("/api/provisions/reference/Section 65")
    assert response.status_code == 200
    data = response.json()
    assert data["provision_id"] == "bsa-2023-section-65"
    assert data["act_short"] == "BSA 2023"


def test_search_theft_finds_bns_provisions():
    response = client.get("/api/provisions", params={"search": "theft"})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 2
    provision_ids = [p["provision_id"] for p in data["provisions"]]
    assert "bns-2023-section-303" in provision_ids


def test_get_bns_section_85_cruelty():
    response = client.get("/api/provisions/reference/Section 85")
    assert response.status_code == 200
    data = response.json()
    assert data["provision_id"] == "bns-2023-section-85"
    assert "cruelty" in data["short_title"].lower()


def test_get_bnss_section_482_anticipatory_bail():
    response = client.get("/api/provisions/reference/Section 482")
    assert response.status_code == 200
    data = response.json()
    assert data["provision_id"] == "bnss-2023-section-482"
    assert "bail" in data["short_title"].lower()


def test_get_bnss_section_126_maintenance():
    response = client.get("/api/provisions/reference/Section 126")
    assert response.status_code == 200
    data = response.json()
    assert data["provision_id"] == "bnss-2023-section-126"
    assert "maintenance" in data["short_title"].lower()


def test_get_bsa_section_24_confession():
    response = client.get("/api/provisions/reference/Section 24")
    assert response.status_code == 200
    data = response.json()
    assert data["provision_id"] == "bsa-2023-section-24"
    assert "confession" in data["short_title"].lower()


def test_ambiguous_reference_returns_404_without_category():
    # "Section 2" exists in both BNSS and BSA; without category filter it should be safely rejected
    response = client.get("/api/provisions/reference/Section 2")
    assert response.status_code == 404


def test_disambiguated_references_with_category_or_act():
    # Disambiguating via query parameter
    res_bnss = client.get("/api/provisions/reference/Section 2?category=bnss")
    assert res_bnss.status_code == 200
    assert res_bnss.json()["provision_id"] == "bnss-2023-section-2"

    res_bsa = client.get("/api/provisions/reference/Section 2?category=bsa")
    assert res_bsa.status_code == 200
    assert res_bsa.json()["provision_id"] == "bsa-2023-section-2"

    # Disambiguating via embedded act name in reference path
    res_embedded = client.get("/api/provisions/reference/BNSS Section 2")
    assert res_embedded.status_code == 200
    assert res_embedded.json()["provision_id"] == "bnss-2023-section-2"


def test_predecessor_reference_mapping():
    # IPC 420 -> BNS Section 318
    res_ipc = client.get("/api/provisions/reference/IPC 420")
    assert res_ipc.status_code == 200
    assert res_ipc.json()["provision_id"] == "bns-2023-section-318"

    # CrPC 438 -> BNSS Section 482
    res_crpc = client.get("/api/provisions/reference/CrPC 438")
    assert res_crpc.status_code == 200
    assert res_crpc.json()["provision_id"] == "bnss-2023-section-482"


def test_multi_token_ranked_search():
    # Multi-token search for anticipatory bail should rank BNSS Section 482 first
    response = client.get("/api/provisions", params={"search": "anticipatory bail"})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    assert data["provisions"][0]["provision_id"] == "bnss-2023-section-482"