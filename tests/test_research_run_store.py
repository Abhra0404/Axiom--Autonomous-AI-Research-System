from uuid import uuid4

from app.core.research_run_store import (
    ResearchRunStore,
)
from app.core.research_loop import ResearchResult
from app.models.events import ResearchEvent
from app.models.schemas import (
    Critique,
    ResearchPlan,
)
from app.models.state import ResearchState


def test_research_run_store_save_and_load(
    tmp_path,
):

    run_id = uuid4()

    plan = ResearchPlan(
        question="Does RAG reduce hallucinations?",
        objectives=[
            "Evaluate hallucination reduction."
        ],
        sub_questions=[
            "What does the evidence show?"
        ],
        search_queries=[
            "RAG hallucination research"
        ],
    )

    critique = Critique(
        sufficient=True,
        overall_confidence=0.9,
        strengths=[
            "Multiple sources support the finding."
        ],
        weaknesses=[],
        missing_information=[],
        follow_up_questions=[],
    )

    state = ResearchState(
        run_id=run_id,
        iteration=1,
        status="completed",
        sources_found=2,
        claims_found=4,
        relationships_found=1,
        confidence=0.9,
    )

    result = ResearchResult(
        plan=plan,
        sources=[],
        analyses=[],
        relationships=[],
        critique=critique,
        iterations=1,
        state=state,
        events=[
            ResearchEvent(
                event="research_completed",
                iteration=1,
            )
        ],
    )

    store = ResearchRunStore(
        str(tmp_path)
    )

    path = store.save(result)

    assert path.exists()

    loaded = store.load(run_id)

    assert loaded["iterations"] == 1

    assert (
        loaded["state"]["status"]
        == "completed"
    )

    assert (
        loaded["critique"]["overall_confidence"]
        == 0.9
    )

    assert len(loaded["events"]) == 1

def test_research_run_store_exists(
    tmp_path,
):

    store = ResearchRunStore(
        str(tmp_path)
    )

    run_id = uuid4()

    assert store.exists(run_id) is False

def test_research_run_store_lists_runs(
    tmp_path,
):

    store = ResearchRunStore(
        str(tmp_path)
    )

    run_id_1 = uuid4()
    run_id_2 = uuid4()

    for run_id in [
        run_id_1,
        run_id_2,
    ]:

        path = (
            tmp_path
            / f"{run_id}.json"
        )

        path.write_text(
            "{}",
            encoding="utf-8",
        )

    runs = store.list_runs()

    assert len(runs) == 2

    assert run_id_1 in runs
    assert run_id_2 in runs