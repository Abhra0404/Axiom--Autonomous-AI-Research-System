from unittest.mock import MagicMock

from app.core.claim_analyzer import ClaimAnalyzer
from app.models.schemas import Claim


def test_claim_analyzer_detects_contradiction():

    llm = MagicMock()

    llm.generate_json.return_value = {
        "relationships": [
            {
                "claim_a": "claim-1",
                "claim_b": "claim-2",
                "relationship": "contradicts",
                "confidence": 0.92,
            }
        ]
    }

    analyzer = ClaimAnalyzer(llm)

    claims = [
        Claim(
            id="claim-1",
            statement="RAG reduces hallucinations.",
            source_id="source-1",
            confidence=0.9,
        ),
        Claim(
            id="claim-2",
            statement="RAG does not reduce hallucinations.",
            source_id="source-2",
            confidence=0.8,
        ),
    ]

    relationships = analyzer.analyze(
        claims
    )

    assert len(relationships) == 1

    assert (
        relationships[0].relationship
        == "contradicts"
    )


def test_claim_analyzer_ignores_invalid_claims():

    llm = MagicMock()

    llm.generate_json.return_value = {
        "relationships": [
            {
                "claim_a": "claim-1",
                "claim_b": "claim-999",
                "relationship": "contradicts",
                "confidence": 0.9,
            }
        ]
    }

    analyzer = ClaimAnalyzer(llm)

    claims = [
        Claim(
            id="claim-1",
            statement="RAG reduces hallucinations.",
            source_id="source-1",
            confidence=0.9,
        )
    ]

    relationships = analyzer.analyze(
        claims
    )

    assert relationships == []

def test_claim_analyzer_detects_duplicate():

    llm = MagicMock()

    llm.generate_json.return_value = {
        "relationships": [
            {
                "claim_a": "claim-1",
                "claim_b": "claim-2",
                "relationship": "duplicate",
                "confidence": 0.95,
            }
        ]
    }

    analyzer = ClaimAnalyzer(llm)

    claims = [
        Claim(
            id="claim-1",
            statement="RAG reduces hallucinations.",
            source_id="source-1",
            confidence=0.9,
        ),
        Claim(
            id="claim-2",
            statement="Retrieval augmentation lowers hallucination rates.",
            source_id="source-2",
            confidence=0.85,
        ),
    ]

    relationships = analyzer.analyze(
        claims
    )

    assert len(relationships) == 1
    assert (
        relationships[0].relationship
        == "duplicate"
    )
    assert (
        relationships[0].confidence
        == 0.95
    )