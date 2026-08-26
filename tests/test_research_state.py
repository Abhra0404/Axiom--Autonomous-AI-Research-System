from uuid import uuid4

from app.models.state import ResearchState


def test_research_state_defaults():

    state = ResearchState(
        run_id=uuid4(),
    )

    assert state.iteration == 0
    assert state.status == "initialized"
    assert state.sources_found == 0
    assert state.claims_found == 0
    assert state.relationships_found == 0
    assert state.confidence == 0.0


def test_research_state_tracks_progress():

    state = ResearchState(
        run_id=uuid4(),
        iteration=2,
        status="running",
        sources_found=8,
        claims_found=17,
        relationships_found=6,
        confidence=0.87,
    )

    assert state.iteration == 2
    assert state.sources_found == 8
    assert state.claims_found == 17
    assert state.relationships_found == 6
    assert state.confidence == 0.87