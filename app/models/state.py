from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ResearchState(BaseModel):
    run_id: UUID
    iteration: int = 0

    status: str = "initialized"

    sources_found: int = 0
    claims_found: int = 0
    relationships_found: int = 0

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    started_at: datetime | None = None
    completed_at: datetime | None = None