from unittest.mock import patch

from app.core.source_cache import SourceCache
from app.core.source_ingestor import SourceIngestor
from app.models.schemas import Source


HTML_CONTENT = """
<html>
    <body>
        <article>
            This is sample research content.
        </article>
    </body>
</html>
"""


@patch("app.core.source_ingestor.trafilatura.fetch_url")
def test_source_ingestion(mock_fetch, tmp_path):

    mock_fetch.return_value = HTML_CONTENT

    cache = SourceCache(str(tmp_path))

    ingestor = SourceIngestor(
        cache=cache
    )

    source = Source(
        id="test-001",
        title="Test Research",
        url="https://example.com",
        source_type="article",
    )

    result = ingestor.ingest(source)

    assert result is not None
    assert result.content is not None
    assert "sample research content" in result.content

    mock_fetch.assert_called_once()


@patch("app.core.source_ingestor.trafilatura.fetch_url")
def test_source_ingestion_uses_cache(
    mock_fetch,
    tmp_path,
):

    mock_fetch.return_value = HTML_CONTENT

    cache = SourceCache(str(tmp_path))

    ingestor = SourceIngestor(
        cache=cache
    )

    source = Source(
        id="test-001",
        title="Test Research",
        url="https://example.com",
        source_type="article",
    )

    # First ingestion → cache miss
    first_result = ingestor.ingest(source)

    assert first_result is not None
    assert mock_fetch.call_count == 1

    # Second ingestion → cache hit
    second_result = ingestor.ingest(source)

    assert second_result is not None

    # No second network request
    assert mock_fetch.call_count == 1

    assert (
        second_result.content
        == first_result.content
    )