from app.core.source_ranker import SourceRanker
from app.models.schemas import Source


def test_source_ranker_ranks_relevant_sources():

    relevant = Source(
        id="1",
        title="Retrieval Augmented Generation and LLM Hallucinations",
        url="https://example.com/rag",
        source_type="paper",
        content=(
            "This paper investigates how RAG affects "
            "hallucinations in large language models."
        ),
    )

    irrelevant = Source(
        id="2",
        title="Introduction to Computer Networks",
        url="https://example.com/networks",
        source_type="article",
        content=(
            "This article discusses TCP, UDP, "
            "routing and network protocols."
        ),
    )

    ranker = SourceRanker()

    results = ranker.rank(
        [irrelevant, relevant],
        "Does RAG reduce hallucinations in LLMs?",
    )

    assert results[0].id == "1"
    assert (
        results[0].relevance_score
        > results[1].relevance_score
    )


def test_source_ranker_selects_top_k():

    sources = [
        Source(
            id=str(i),
            title=f"Source {i}",
            url=f"https://example.com/{i}",
            source_type="article",
            content="Research content",
        )
        for i in range(5)
    ]

    ranker = SourceRanker()

    ranked = ranker.rank(
        sources,
        "research",
    )

    selected = ranker.select(
        ranked,
        top_k=3,
    )

    assert len(selected) == 3

def test_source_ranker_assigns_quality_score():

    sources = [
        Source(
            id="paper",
            title="RAG hallucination research",
            url="https://example.com/paper",
            source_type="paper",
            content="RAG hallucination research.",
        ),
        Source(
            id="article",
            title="RAG hallucination research",
            url="https://example.com/article",
            source_type="article",
            content="RAG hallucination research.",
        ),
    ]

    ranker = SourceRanker()

    results = ranker.rank(
        sources,
        "RAG hallucination research",
    )

    assert results[0].quality_score == 1.0
    assert results[1].quality_score == 0.45