from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ResearchEvent(BaseModel):
    event: str
    iteration: int
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )
    data: dict[str, Any] = Field(
        default_factory=dict
    )