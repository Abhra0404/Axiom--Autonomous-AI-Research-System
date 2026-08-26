from unittest.mock import MagicMock

from app.agents.evidence import EvidenceAgent
from app.models.schemas import Source


def test_evidence_agent_returns_structured_analysis():

    llm = MagicMock()

    llm.generate_json.return_value = {
        "claims": [
            {
                "id": "claim-1",
                "statement": "RAG can reduce hallucinations.",
                "source_id": "source-1",
                "confidence": 0.9,
            }
        ],
        "evidence": [
            {
                "id": "evidence-1",
                "claim_id": "claim-1",
                "source_id": "source-1",
                "content": "The study reported reduced hallucination rates.",
                "strength": "strong",
            }
        ],
    }

    agent = EvidenceAgent(llm)

    source = Source(
        id="source-1",
        title="RAG Study",
        url="https://example.com",
        source_type="paper",
        content="RAG was evaluated for hallucination reduction.",
    )

    result = agent.analyze(source)

    assert len(result.claims) == 1
    assert len(result.evidence) == 1

    assert result.claims[0].statement == "RAG can reduce hallucinations."
    assert result.claims[0].confidence == 0.9

    assert result.evidence[0].strength == "strong"

from app.core.evidence_cache import EvidenceCache


def test_evidence_agent_uses_cache(tmp_path):

    llm = MagicMock()

    llm.generate_json.return_value = {
        "claims": [
            {
                "id": "claim-1",
                "statement": "RAG can reduce hallucinations.",
                "source_id": "source-1",
                "confidence": 0.9,
                "evidence_ids": [
                    "evidence-1"
                ],
            }
        ],
        "evidence": [
            {
                "id": "evidence-1",
                "claim_id": "claim-1",
                "source_id": "source-1",
                "content": "The study reported fewer hallucinations.",
                "strength": "strong",
                "location": "paragraph 4",
            }
        ],
    }

    cache = EvidenceCache(
        str(tmp_path)
    )

    agent = EvidenceAgent(
        llm,
        cache=cache,
    )

    source = Source(
        id="source-1",
        title="RAG Study",
        url="https://example.com",
        source_type="paper",
        content="RAG was evaluated for hallucination reduction.",
    )

    # First call → Gemini should be called
    first_result = agent.analyze(source)

    assert first_result is not None
    assert llm.generate_json.call_count == 1

    # Second call → cache should be used
    second_result = agent.analyze(source)

    assert second_result is not None

    # Gemini must NOT be called again
    assert llm.generate_json.call_count == 1

    assert (
        second_result.claims[0].statement
        == first_result.claims[0].statement
    )