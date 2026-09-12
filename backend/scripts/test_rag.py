from app.services.rag_service import RAGService


def main() -> None:
    rag = RAGService()

    queries = [
    "What is the right to life?",
    "privacy rights",
    "freedom of speech",
    "How do I repair my bicycle?",
]

    for query in queries:
        print("\n" + "=" * 60)
        print(f"Query: {query}")

        results = rag.search(query, top_k=3)

        for result in results:
            provision = result["provision"]

            print(
                f"- {provision.reference_number}"
                f" | {provision.provision_id}"
                f" | verification={provision.verification_status.value}"
                f" | distance={result['distance']}"
            )


if __name__ == "__main__":
    main()