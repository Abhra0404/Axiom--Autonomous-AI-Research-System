from pydantic import BaseModel, Field


class ResearchRequestAPI(BaseModel):
    topic: str = Field(
        min_length=5,
        max_length=500,
    )

    depth: str = "deep"


class ResearchResponse(BaseModel):
    run_id: str
    status: str
    confidence: float
    sufficient: bool