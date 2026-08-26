from unittest.mock import MagicMock

from app.agents.critic import CriticAgent
from app.models.schemas import (
    ClaimRelationship,
    ResearchPlan,
)


def test_critic_rejects_strong_contradiction():

    llm = MagicMock()

    llm.generate_json.return_value = {
        "sufficient": True,
        "overall_confidence": 0.95,
        "strengths": [
            "Multiple sources were found."
        ],
        "weaknesses": [],
        "missing_information": [],
        "follow_up_questions": [],
    }

    critic = CriticAgent(llm)

    relationships = [
        ClaimRelationship(
            claim_a="claim-1",
            claim_b="claim-2",
            relationship="contradicts",
            confidence=0.92,
        )
    ]

    plan = ResearchPlan(
        question="Does RAG reduce hallucinations in LLMs?",
        objectives=[
            "Determine whether RAG reduces hallucinations."
        ],
        sub_questions=[
            "How does RAG affect hallucination rates?",
        ],
        search_queries=[
            "RAG hallucinations LLM research",
        ],
    )

    result = critic.critique(
        plan=plan,
        sources=[],
        analyses=[],
        relationships=relationships,
    )

    assert result.sufficient is False

    assert (
        "Conflicting evidence requires further research."
        in result.weaknesses
    )