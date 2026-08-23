from unittest.mock import MagicMock

from app.core.research_loop import ResearchLoop
from app.models.schemas import (
    Claim,
    Critique,
    Evidence,
    EvidenceAnalysis,
    ResearchPlan,
    Source,
)


def test_research_loop_stops_when_sufficient():

    planner = MagicMock()
    researcher = MagicMock()
    evidence_agent = MagicMock()
    critic = MagicMock()
    ranker = MagicMock()

    plan = ResearchPlan(
        question="Does RAG reduce hallucinations?",
        objectives=[
            "Evaluate RAG effectiveness."
        ],
        sub_questions=[
            "What does the evidence show?"
        ],
        search_queries=[
            "RAG hallucination research"
        ],
    )

    source = Source(
        id="source-1",
        title="RAG Study",
        url="https://example.com",
        source_type="paper",
        content="RAG reduces hallucinations.",
    )

    analysis = EvidenceAnalysis(
        claims=[
            Claim(
                id="claim-1",
                statement="RAG reduces hallucinations.",
                source_id="source-1",
                confidence=0.9,
            )
        ],
        evidence=[
            Evidence(
                id="evidence-1",
                claim_id="claim-1",
                source_id="source-1",
                content="Study evidence.",
                strength="strong",
            )
        ],
    )

    researcher.search.return_value = [
        source
    ]

    ranker.rank.return_value = [
        source
    ]

    ranker.select.return_value = [
        source
    ]

    evidence_agent.analyze.return_value = (
        analysis
    )

    critic.critique.return_value = Critique(
        sufficient=True,
        overall_confidence=0.9,
        strengths=["Strong evidence."],
        weaknesses=[],
        missing_information=[],
        follow_up_questions=[],
    )

    loop = ResearchLoop(
        planner=planner,
        researcher=researcher,
        evidence_agent=evidence_agent,
        critic=critic,
        source_ranker=ranker,
        max_iterations=3,
    )

    result = loop.run(plan)

    assert result.iterations == 1
    assert result.critique.sufficient is True
    assert len(result.sources) == 1