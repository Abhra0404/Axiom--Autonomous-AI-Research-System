from app.models.schemas import ResearchRequest


def test_research_request():
    request = ResearchRequest(
        topic="Does RAG reduce hallucinations in LLMs?",
        depth="deep",
    )

    assert request.topic == "Does RAG reduce hallucinations in LLMs?"
    assert request.depth == "deep"