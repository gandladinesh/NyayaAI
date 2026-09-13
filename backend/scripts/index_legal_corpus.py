"""
NyayaAI — Index Legal Corpus

Loads the curated legal seed corpus and indexes it into ChromaDB.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.legal_provision_service import LegalProvisionService
from app.services.rag_service import RAGService


def main() -> None:
    legal_service = LegalProvisionService()
    rag_service = RAGService()

    provisions = legal_service.get_all()

    print(f"Loaded provisions: {len(provisions)}")

    indexed = rag_service.index_provisions(provisions)

    print(f"Indexed provisions: {indexed}")
    print(f"ChromaDB count: {rag_service.collection_count()}")


if __name__ == "__main__":
    main()