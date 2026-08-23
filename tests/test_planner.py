from app.agents.planner import Planner
from app.models.schemas import ResearchRequest


def test_planner_creates_research_plan():
    request = ResearchRequest(
        topic="Does RAG reduce hallucinations in LLMs?",
        depth="deep",
    )

    planner = Planner()
    plan = planner.create_plan(request)

    assert plan.question == request.topic
    assert len(plan.objectives) > 0
    assert len(plan.sub_questions) > 0
    assert len(plan.search_queries) > 0