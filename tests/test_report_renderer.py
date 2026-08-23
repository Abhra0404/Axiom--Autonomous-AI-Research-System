from app.core.report_renderer import ReportRenderer
from app.models.schemas import ResearchReport


def test_report_renderer():

    report = ResearchReport(
        title="RAG Research",
        executive_summary="RAG may reduce hallucinations.",
        research_question="Does RAG reduce hallucinations?",
        methodology="Reviewed multiple sources.",
        key_findings=[
            "Evidence suggests a reduction."
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