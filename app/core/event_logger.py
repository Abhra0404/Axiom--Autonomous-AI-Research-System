from app.models.events import ResearchEvent


class ResearchEventLogger:

    def __init__(self):
        self.events: list[ResearchEvent] = []

    def emit(
        self,
        event: str,
        iteration: int,
        data: dict | None = None,
    ) -> ResearchEvent:

        research_event = ResearchEvent(
            event=event,
            iteration=iteration,
            data=data or {},
        )

        self.events.append(
            research_event
        )

        return research_event

    def all(self) -> list[ResearchEvent]:
        return list(self.events)

    def clear(self) -> None:
        self.events.clear()