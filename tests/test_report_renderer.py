from app.core.report_renderer import ReportRenderer
from app.models.schemas import ResearchReport
from app.models.schemas import ReportFinding
from app.models.schemas import (
    Claim,
    Source,
)

def test_report_renderer():

    report = ResearchReport(
        title="RAG Research",
        executive_summary="RAG may reduce hallucinations.",
        research_question="Does RAG reduce hallucinations?",
        methodology="Reviewed multiple sources.",
        key_findings=[
            ReportFinding(
                statement="Evidence suggests a reduction.",
                claim_ids=[],
            )
        ],
        evidence_analysis=[
            "Several sources reported improvements."
        ],
        limitations=[
            "Studies vary in methodology."
        ],
        conclusion="RAG appears promising.",
        sources=[
            "https://example.com/paper"
        ],
    )

    renderer = ReportRenderer()

    result = renderer.render(report)

    assert "# RAG Research" in result
    assert "## Executive Summary" in result
    assert "## Key Findings" in result
    assert "## Conclusion" in result
    assert "https://example.com/paper" in result

def test_report_renderer_adds_citations():

    report = ResearchReport(
        title="RAG Research",
        executive_summary="RAG may reduce hallucinations.",
        research_question="Does RAG reduce hallucinations?",
        methodology="Reviewed multiple sources.",
        key_findings=[
            ReportFinding(
                statement="RAG reduces hallucinations.",
                claim_ids=[
                    "claim-1",
                ],
            )
        ],
        evidence_analysis=[
            "A study reported fewer hallucinations."
        ],
        limitations=[
            "Studies vary in methodology."
        ],
        conclusion="RAG appears promising.",
        sources=[
            "https://example.com/paper"
        ],
    )

    source = Source(
        id="source-1",
        title="RAG Study",
        url="https://example.com/paper",
        source_type="paper",
        content="Research content.",
    )

    claim = Claim(
        id="claim-1",
        statement="RAG reduces hallucinations.",
        source_id="source-1",
        confidence=0.9,
    )

    renderer = ReportRenderer()

    result = renderer.render(
        report,
        sources=[source],
        claims=[claim],
    )

    assert (
        "RAG reduces hallucinations. [1]"
        in result
    )

    assert (
        "[1] RAG Study — https://example.com/paper"
        in result
    )