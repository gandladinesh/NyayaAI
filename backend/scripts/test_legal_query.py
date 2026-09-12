from app.services.legal_query_service import LegalQueryService


def main() -> None:
    service = LegalQueryService()

    questions = [
        "What is the right to life?",
        "What is freedom of speech?",
        "How do I repair my bicycle?",
    ]

    for question in questions:
        print("\n" + "=" * 70)
        print(f"Question: {question}")

        response = service.answer(question)

        print(f"Status: {response['status']}")

        primary = response["primary_result"]

        if primary:
            print("\nPRIMARY RESULT")
            print(f"Reference: {primary['reference_number']}")
            print(f"Verification: {primary['verification_status']}")
            print(f"Exact text: {primary['exact_text']}")
            print(f"AI explanation: {primary['ai_explanation']}")
            print(f"Distance: {primary['distance']}")

        related = response["related_results"]

        if related:
            print("\nRELATED RESULTS")

            for result in related:
                print(
                    f"- {result['reference_number']}"
                    f" | distance={result['distance']}"
                )

        if not primary:
            print(f"Message: {response['message']}")


if __name__ == "__main__":
    main()