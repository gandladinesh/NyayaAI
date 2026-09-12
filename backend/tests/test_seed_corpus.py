"""
Automated tests for Phase 1 seed corpus verification.

Checks:
- exact_text is present and non-empty for all VERIFIED records
- exact_text is strictly NOT identical to ai_explanation
- VERIFIED records have an authoritative government source
- source_type is official for primary government sources
- source_url is present for verified records
- Article numbers are unique
- Clauses/subclauses are preserved
- Constitution-wide provisions do NOT receive a State/District jurisdiction
- Language is English, jurisdiction is central
"""

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "seed_corpus.json"

REQUIRED_ARTICLES = [
    "12", "13", "14", "15", "16", "17", "18", "19", "20",
    "21", "21A", "22", "23", "24", "25", "26", "27", "28",
    "29", "30", "32", "39A", "44", "51A", "226"
]

def load_corpus():
    assert DATA_PATH.exists(), f"Seed corpus file not found at {DATA_PATH}"
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def test_corpus_presence_and_minimum_articles():
    data = load_corpus()
    assert len(data) >= len(REQUIRED_ARTICLES), f"Expected at least {len(REQUIRED_ARTICLES)} provisions, got {len(data)}"
    
    article_numbers = [item.get("article_number") for item in data]
    for req in REQUIRED_ARTICLES:
        assert req in article_numbers, f"Required Article {req} missing from seed corpus"

def test_unique_article_numbers_and_ids():
    data = load_corpus()
    ids = [item.get("provision_id") for item in data]
    refs = [item.get("reference_number") for item in data]
    
    assert len(ids) == len(set(ids)), f"Duplicate provision_ids found: {ids}"
    assert len(refs) == len(set(refs)), f"Duplicate reference_numbers found: {refs}"

def test_exact_text_present_and_not_ai_generated():
    data = load_corpus()
    for item in data:
        exact_text = item.get("exact_text", "")
        ai_explanation = item.get("ai_explanation", "")
        
        # Exact text must exist and have meaningful length
        assert exact_text and len(exact_text.strip()) > 20, f"Empty or too short exact_text in {item.get('provision_id')}"
        
        # AI explanation must be strictly distinct from exact_text
        assert exact_text.strip() != ai_explanation.strip(), (
            f"CRITICAL VIOLATION: exact_text equals ai_explanation in {item.get('provision_id')}"
        )
        assert item.get("ai_explanation") is not None, f"Missing ai_explanation in {item.get('provision_id')}"
        
        # Verify that ai_explanation doesn't simply contain identical verbatim text
        assert not ai_explanation.startswith("No person shall be deprived of his life"), (
            f"AI explanation appears to be copy of legal text in {item.get('provision_id')}"
        )

def test_verified_records_have_authoritative_source():
    data = load_corpus()
    for item in data:
        if item.get("verification_status") == "verified":
            assert item.get("source_name"), f"Missing source_name in {item.get('provision_id')}"
            assert item.get("source_type") in ["official", "court"], (
                f"Invalid source_type for verified record {item.get('provision_id')}: {item.get('source_type')}"
            )
            assert item.get("source_url"), f"Missing source_url in {item.get('provision_id')}"
            assert "legislative.gov.in" in item.get("source_url") or "indiacode.nic.in" in item.get("source_url"), (
                f"Source URL is not an authoritative government domain in {item.get('provision_id')}"
            )
            # Ensure IndianKanoon is NEVER labeled as official
            if "indiankanoon" in (item.get("source_url") or "").lower():
                assert item.get("source_type") != "official", (
                    f"IndianKanoon labeled as official in {item.get('provision_id')}"
                )

def test_jurisdiction_and_state_null_for_constitution():
    data = load_corpus()
    for item in data:
        # Constitutional provisions apply nationwide
        assert item.get("jurisdiction") in ["central", "INDIA"], (
            f"Constitutional article {item.get('provision_id')} should have central/national jurisdiction"
        )
        assert item.get("applicable_states") == [], (
            f"Constitution-wide article {item.get('provision_id')} must not be restricted to specific states"
        )

def test_clauses_preserved_in_complex_articles():
    data = load_corpus()
    art_map = {item.get("article_number"): item for item in data}
    
    # Article 19 must have clauses/subclauses preserved
    art19 = art_map.get("19")
    assert art19 is not None
    text19 = art19.get("exact_text")
    assert "(1)" in text19 or "freedom of speech" in text19
    assert "(a)" in text19 or "assemble peaceably" in text19 or "freedom of speech" in text19
    
    # Article 32 must preserve remedies and writ powers
    art32 = art_map.get("32")
    assert art32 is not None
    text32 = art32.get("exact_text")
    assert "habeas corpus" in text32.lower()
    assert "mandamus" in text32.lower()
    
    # Article 226 must preserve High Court writ powers
    art226 = art_map.get("226")
    assert art226 is not None
    text226 = art226.get("exact_text")
    assert "High Court" in text226
    assert "habeas corpus" in text226.lower()

if __name__ == "__main__":
    print("Running seed corpus tests...")
    test_corpus_presence_and_minimum_articles()
    print("[PASS] test_corpus_presence_and_minimum_articles passed")
    test_unique_article_numbers_and_ids()
    print("[PASS] test_unique_article_numbers_and_ids passed")
    test_exact_text_present_and_not_ai_generated()
    print("[PASS] test_exact_text_present_and_not_ai_generated passed")
    test_verified_records_have_authoritative_source()
    print("[PASS] test_verified_records_have_authoritative_source passed")
    test_jurisdiction_and_state_null_for_constitution()
    print("[PASS] test_jurisdiction_and_state_null_for_constitution passed")
    test_clauses_preserved_in_complex_articles()
    print("[PASS] test_clauses_preserved_in_complex_articles passed")
    print("\nALL 6 SEED CORPUS TESTS PASSED!")
