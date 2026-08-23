from unittest.mock import MagicMock

from app.agents.critic import CriticAgent
from app.models.schemas import (
    Critique,
    Evidence,
    EvidenceAnalysis,
    Claim,
    ResearchPlan,
    Source,
)


def test_critic_returns_critique():

    llm = MagicMock()

    llm.generate_json.return_value = {
        "sufficient": False,
        "overall_confidence": 0.65,
        "strengths": [
            "Multiple sources support the main claim."
        ],
        "weaknesses": [
            "Evidence is limited."
        ],
        "missing_information": [
            "Large-scale studies."
        ],
        "follow_up_questions": [
            "Are there larger studies?"
        ],
    }

    agent = CriticAgent(llm)

    plan = ResearchPlan(
        question="Does RAG reduce hallucinations?",
        objectives=[
            "Evaluate whether RAG reduces hallucinations."
        ],
        sub_questions=[
            "What does the evidence show?"
        ],
        search_queries=[
            "RAG hallucinations research"
        ],
    )

    source = Source(
        id="source-1",
        title="RAG Study",
        url="https://example.com",
        source_type="paper",
        content="RAG was evaluated.",
    )

    analysis = EvidenceAnalysis(
        claims=[
            Claim(
                id="claim-1",
                statement="RAG reduced hallucinations.",
                source_id="source-1",
                confidence=0.8,
            )
        ],
        evidence=[
            Evidence(
                id="evidence-1",
                claim_id="claim-1",
                source_id="source-1",
                content="The study reported fewer hallucinations.",
                strength="moderate",
            )
        ],
    )

    result = agent.critique(
        plan,
        [source],
        [analysis],
    )

    assert result.sufficient is False
    assert result.overall_confidence == 0.65
    assert len(result.weaknesses) > 0
    assert len(result.follow_up_questions) > 0