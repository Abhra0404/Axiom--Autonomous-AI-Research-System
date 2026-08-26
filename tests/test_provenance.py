from app.core.provenance import ProvenanceResolver
from app.models.schemas import (
    Claim,
    Evidence,
    Source,
)


def test_provenance_resolves_claim_evidence():

    source = Source(
        id="source-1",
        title="RAG Study",
        url="https://example.com",
        source_type="paper",
        content="Research content.",
    )

    claim = Claim(
        id="claim-1",
        statement="RAG reduces hallucinations.",
        source_id="source-1",
        confidence=0.9,
        evidence_ids=[
            "evidence-1",
        ],
    )

    evidence = Evidence(
        id="evidence-1",
        claim_id="claim-1",
        source_id="source-1",
        content="The study reported reduced hallucinations.",
        strength="strong",
        location="paragraph 4",
    )

    resolver = ProvenanceResolver(
        [source],
        [claim],
        [evidence],
    )

    result = resolver.get_claim_evidence(
        claim
    )

    assert len(result) == 1
    assert result[0].id == "evidence-1"
    assert result[0].location == "paragraph 4"


def test_provenance_resolves_source():

    source = Source(
        id="source-1",
        title="RAG Study",
        url="https://example.com",
        source_type="paper",
        content="Research content.",
    )

    claim = Claim(
        id="claim-1",
        statement="RAG reduces hallucinations.",
        source_id="source-1",
        confidence=0.9,
    )

    resolver = ProvenanceResolver(
        [source],
        [claim],
        [],
    )

    result = resolver.get_claim_source(
        claim
    )

    assert result is not None
    assert result.title == "RAG Study"