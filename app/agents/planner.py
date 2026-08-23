from app.models.schemas import ResearchPlan, ResearchRequest


class Planner:
    def create_plan(self, request: ResearchRequest) -> ResearchPlan:
        return ResearchPlan(
            question=request.topic,
            objectives=[
                f"Investigate the current state of research on: {request.topic}",
                "Identify major findings and competing perspectives",
                "Evaluate the quality of available evidence",
            ],
            sub_questions=[
                f"What is currently known about {request.topic}?",
                f"What are the main arguments or findings related to {request.topic}?",
                f"What limitations or gaps exist in the current research?",
            ],
            search_queries=[
                request.topic,
                f"{request.topic} research paper",
                f"{request.topic} study",
                f"{request.topic} benchmark",
            ],
        )