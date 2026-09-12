from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_all_provisions():
    response = client.get("/api/provisions")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 25
    assert len(data["provisions"]) == 25


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