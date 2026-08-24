from app.core.source_cache import SourceCache
from app.models.schemas import Source


def test_source_cache(tmp_path):

    cache = SourceCache(
        str(tmp_path)
    )

    source = Source(
        id="source-1",
        title="Test Source",
        url="https://example.com/test",
        source_type="article",
        content="Test content",
    )

    cache.set(source)

    result = cache.get(
        "https://example.com/test"
    )

    assert result is not None
    assert result.id == "source-1"
    assert result.content == "Test content"


def test_source_cache_miss(tmp_path):

    cache = SourceCache(
        str(tmp_path)
    )

    result = cache.get(
        "https://example.com/missing"
    )

    assert result is None