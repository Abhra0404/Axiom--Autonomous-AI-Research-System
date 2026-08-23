from datetime import datetime, timezone

from app.core.run_store import RunStore
from app.models.schemas import ResearchPlan, ResearchRun


def test_run_store_saves_run(tmp_path):

    plan = ResearchPlan(
        question="Test question",
        objectives=["Test objective"],
        sub_questions=["Test sub-question"],
        search_queries=["test query"],
    )

    run = ResearchRun(
        id="run_test",
        question="Test question",
        created_at=datetime.now(timezone.utc),
        plan=plan,
        sources=[],
        analyses=[],
    )

    store = RunStore(str(tmp_path))

    path = store.save(run)

    assert path.exists()
    assert path.name == "run.json"

    content = path.read_text()

    assert "Test question" in content