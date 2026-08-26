from app.core.evidence_cache import EvidenceCache
from app.models.schemas import (
    Claim,
    Evidence,
    EvidenceAnalysis,
)


def test_evidence_cache(tmp_path):

    cache = EvidenceCache(
        str(tmp_path)
    )

    analysis = EvidenceAnalysis(
        source_id="source-1",
        claims=[
            Claim(
                id="claim-1",
                statement="RAG can reduce hallucinations.",
                source_id="source-1",
                confidence=0.9,
            )
        ],
        evidence=[
            Evidence(
                id="evidence-1",
                claim_id="claim-1",
                source_id="source-1",
                content="Study reported fewer hallucinations.",
                strength="strong",
            )
        ],
    )

    content = "Research source content."

    cache.set(
        content,
        analysis,
    )

    result = cache.get(content)

    assert result is not None
    assert len(result.claims) == 1
    assert len(result.evidence) == 1
    assert (
        result.claims[0].statement
        == "RAG can reduce hallucinations."
    )


def test_evidence_cache_miss(tmp_path):

    cache = EvidenceCache(
        str(tmp_path)
    )

    result = cache.get(
        "unknown content"
    )

    assert result is None