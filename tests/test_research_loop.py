from unittest.mock import MagicMock

from app.core.research_loop import ResearchLoop
from app.models.schemas import (
    Claim,
    Critique,
    EvidenceAnalysis,
    ResearchPlan,
    Source,
)
from app.core.event_logger import ResearchEventLogger


def test_research_loop_stops_when_sufficient():

    # ---------------------------------------------------------
    # Mock researcher
    # ---------------------------------------------------------

    researcher = MagicMock()

    source = Source(
        id="source-1",
        title="RAG Study",
        url="https://example.com/research",
        source_type="paper",
        content="RAG research content.",
    )

    researcher.search.return_value = [
        source
    ]

    # ---------------------------------------------------------
    # Mock evidence agent
    # ---------------------------------------------------------

    evidence_agent = MagicMock()

    claim = Claim(
        id="claim-1",
        statement="RAG can reduce hallucinations.",
        source_id="source-1",
        confidence=0.9,
        evidence_ids=[],
    )

    analysis = EvidenceAnalysis(
        claims=[claim],
        evidence=[],
    )

    evidence_agent.analyze.return_value = analysis

    # ---------------------------------------------------------
    # Mock claim analyzer
    # ---------------------------------------------------------

    claim_analyzer = MagicMock()

    claim_analyzer.analyze.return_value = []

    # ---------------------------------------------------------
    # Mock critic
    # ---------------------------------------------------------

    critic = MagicMock()

    critic.critique.return_value = Critique(
        sufficient=True,
        overall_confidence=0.90,
        strengths=[
            "Evidence directly addresses the research question."
        ],
        weaknesses=[],
        missing_information=[],
        follow_up_questions=[],
    )

    # ---------------------------------------------------------
    # Mock planner
    # ---------------------------------------------------------

    planner = MagicMock()

    # ---------------------------------------------------------
    # Mock source ranker
    # ---------------------------------------------------------

    source_ranker = MagicMock()

    source_ranker.rank.return_value = [
        source
    ]

    source_ranker.select.return_value = [
        source
    ]

    event_logger = ResearchEventLogger()

    # ---------------------------------------------------------
    # Research loop
    # ---------------------------------------------------------

    loop = ResearchLoop(
        planner=planner,
        researcher=researcher,
        source_ranker=source_ranker,
        evidence_agent=evidence_agent,
        claim_analyzer=claim_analyzer,
        critic=critic,
        event_logger=event_logger,
    )

    # ---------------------------------------------------------
    # Research plan
    # ---------------------------------------------------------

    plan = ResearchPlan(
        question="Does RAG reduce hallucinations in LLMs?",
        objectives=[
            "Determine whether RAG reduces hallucinations."
        ],
        sub_questions=[
            "How does RAG affect hallucination rates?",
            "What evidence supports or contradicts this?",
        ],
        search_queries=[
            "RAG hallucinations LLM research"
        ],
    )

    # ---------------------------------------------------------
    # Run
    # ---------------------------------------------------------

    result = loop.run(plan)

    event_names = [
        event.event
        for event in result.events
    ]

    assert "research_started" in event_names
    assert "iteration_started" in event_names
    assert "iteration_completed" in event_names
    assert "research_completed" in event_names

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assert result is not None

    assert result.iterations == 1

    assert len(result.sources) == 1

    assert len(result.analyses) == 1

    assert len(result.relationships) == 0

    assert result.critique is not None

    assert result.critique.sufficient is True

    assert (
        result.critique.overall_confidence
        == 0.90
    )
    assert result.state is not None
    assert result.state.status == "completed"
    assert result.state.iteration == 1
    assert result.state.sources_found == 1
    assert result.state.claims_found == 1
    assert result.state.relationships_found == 0
    assert result.state.confidence == 0.90
    assert result.events is not None
    assert len(result.events) >= 3
    assert (
        result.events
        == event_logger.all()
    )
    assert (
        len(event_logger.events)
        == len(result.events)
    )
    researcher.search.assert_called_once()

    evidence_agent.analyze.assert_called_once_with(
        source
    )

    claim_analyzer.analyze.assert_called_once_with(
        [claim]
    )

    critic.critique.assert_called_once()