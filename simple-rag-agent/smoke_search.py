"""Real embedding check, no Anthropic credentials or calls."""
from pathlib import Path

from retrieval import SemanticIndex


def main():
    index = SemanticIndex(Path(__file__).resolve().parent / "docs")
    cases = [
        ("Reimbursement when storms prevent my journey", "04-weather-refunds.md"),
        ("Step-free travel with a mobility chair when the water is low", "05-accessibility.md"),
        ("Transporting refrigerated prescriptions to the island", "06-cargo.md"),
        ("Erasure of personal information and retention of financial data", "08-booking-privacy.md"),
    ]
    for query, expected in cases:
        hits = index.search(query)
        sources = [hit["source"] for hit in hits]
        assert any(source.startswith(expected + "#") for source in sources), (query, sources)
        print(f"PASS: {query} -> {', '.join(sources)}")
    print(f"Validated {len(cases)} paraphrases across {len(index.chunks)} chunks.")


if __name__ == "__main__":
    main()
