from app.models.events import ResearchEvent


def test_research_event_defaults():

    event = ResearchEvent(
        event="iteration_started",
        iteration=1,
    )

    assert event.event == "iteration_started"
    assert event.iteration == 1
    assert event.timestamp is not None
    assert event.data == {}


def test_research_event_stores_data():

    event = ResearchEvent(
        event="iteration_completed",
        iteration=2,
        data={
            "sources": 5,
            "claims": 10,
            "confidence": 0.91,
        },
    )

    assert event.data["sources"] == 5
    assert event.data["claims"] == 10
    assert event.data["confidence"] == 0.91