from app.core.source_quality import SourceQualityScorer
from app.models.schemas import Source


def test_paper_has_high_quality():

    source = Source(
        id="1",
        title="Research Paper",
        url="https://example.com/paper",
        source_type="paper",
    )

    scorer = SourceQualityScorer()

    assert scorer.score(source) == 1.0


def test_documentation_has_high_quality():

    source = Source(
        id="2",
        title="Official Documentation",
        url="https://example.com/docs",
        source_type="documentation",
    )

    scorer = SourceQualityScorer()

    assert scorer.score(source) == 0.9


def test_article_has_medium_quality():

    source = Source(
        id="3",
        title="Technical Article",
        url="https://example.com/article",
        source_type="article",
    )

    scorer = SourceQualityScorer()

    assert scorer.score(source) == 0.45


def test_unknown_source_has_low_quality():

    source = Source(
        id="4",
        title="Unknown Source",
        url="https://example.com",
        source_type="other",
    )

    scorer = SourceQualityScorer()

    assert scorer.score(source) == 0.3


def test_apply_adds_quality_score():

    source = Source(
        id="5",
        title="Research Report",
        url="https://example.com/report",
        source_type="report",
    )

    scorer = SourceQualityScorer()

    result = scorer.apply(source)

    assert result.quality_score == 0.85

def test_arxiv_has_high_quality():

    source = Source(
        id="6",
        title="Research Paper",
        url="https://arxiv.org/abs/2401.12345",
        source_type="article",
    )

    scorer = SourceQualityScorer()

    assert scorer.score(source) == 1.0


def test_subdomain_is_detected():

    source = Source(
        id="7",
        title="Research",
        url="https://blog.arxiv.org/test",
        source_type="article",
    )

    scorer = SourceQualityScorer()

    assert scorer.score(source) == 1.0


def test_github_has_good_quality():

    source = Source(
        id="8",
        title="Research Code",
        url="https://github.com/example/project",
        source_type="article",
    )

    scorer = SourceQualityScorer()

    assert scorer.score(source) == 0.8