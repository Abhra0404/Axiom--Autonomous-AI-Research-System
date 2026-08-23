from unittest.mock import patch

from app.core.source_ingestor import SourceIngestor
from app.models.schemas import Source


@patch("app.core.source_ingestor.trafilatura.fetch_url")
def test_source_ingestion(mock_fetch):
    mock_fetch.return_value = "This is sample research content."

    source = Source(
        id="test-001",
        title="Test Research",
        url="https://example.com",
        source_type="article",
    )

    ingestor = SourceIngestor()
    result = ingestor.ingest(source)

    assert result.content == "This is sample research content."
    