from app.core.event_logger import ResearchEventLogger


def test_event_logger_emits_event():

    logger = ResearchEventLogger()

    event = logger.emit(
        event="iteration_started",
        iteration=1,
    )

    assert event.event == "iteration_started"
    assert event.iteration == 1

    assert len(logger.events) == 1


def test_event_logger_stores_event_data():

    logger = ResearchEventLogger()

    logger.emit(
        event="iteration_completed",
        iteration=1,
        data={
            "sources": 5,
            "claims": 10,
        },
    )

    events = logger.all()

    assert len(events) == 1
    assert events[0].data["sources"] == 5
    assert events[0].data["claims"] == 10


def test_event_logger_clear():

    logger = ResearchEventLogger()

    logger.emit(
        event="research_started",
        iteration=0,
    )

    logger.clear()

    assert logger.all() == []