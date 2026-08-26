from datetime import date
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=5)
    depth: Literal["quick", "standard", "deep"] = "standard"


class ResearchPlan(BaseModel):
    question: str
    objectives: list[str]
    sub_questions: list[str]
    search_queries: list[str]


class Source(BaseModel):
    id: str
    title: str
    url: HttpUrl
    source_type: Literal[
        "paper",
        "documentation",
        "article",
        "report",
        "dataset",
        "other",
    ]
    authors: list[str] = []
    published_date: date | None = None
    content: str | None = None
    retrieved_at: datetime | None = None
    search_query: str | None = None
    relevance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
)


class Claim(BaseModel):
    id: str
    statement: str
    source_id: str
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )
    evidence_ids: list[str] = Field(
        default_factory=list,
    )


class Evidence(BaseModel):
    id: str
    claim_id: str
    source_id: str
    content: str
    strength: Literal[
        "weak",
        "moderate",
        "strong",
    ]
    location: str | None = None

class EvidenceAnalysis(BaseModel):
    claims: list[Claim]
    evidence: list[Evidence]


class ResearchReport(BaseModel):
    title: str
    executive_summary: str
    research_question: str
    methodology: str
    key_findings: list[str]
    evidence_analysis: list[str]
    limitations: list[str]
    conclusion: str
    sources: list[str]

class ResearchRun(BaseModel):
    id: str
    question: str
    created_at: datetime
    plan: ResearchPlan
    sources: list[Source]
    analyses: list[EvidenceAnalysis]

class Critique(BaseModel):
    sufficient: bool
    overall_confidence: float = Field(
        ge=0.0,
        le=1.0,
    )
    strengths: list[str]
    weaknesses: list[str]
    missing_information: list[str]
    follow_up_questions: list[str]

class ReportSection(BaseModel):
    title: str
    content: str

class ReportFinding(BaseModel):
    statement: str
    claim_ids: list[str] = Field(
        default_factory=list,
    )

class ResearchReport(BaseModel):
    title: str
    executive_summary: str
    research_question: str
    methodology: str
    key_findings: list[ReportFinding]
    evidence_analysis: list[str]
    limitations: list[str]
    conclusion: str
    sources: list[str]

