from app.core.source_manager import SourceManager
from app.models.schemas import Source


def test_source_manager_removes_duplicates():

    source_1 = Source(
        id="1",
        title="Research Paper",
        url="https://example.com/paper",
        source_type="paper",
        content="Research content",
    )

    source_2 = Source(
        id="2",
        title="Research Paper",
        url="https://example.com/paper/",
        source_type="paper",
        content="Research content",
    )

    manager = SourceManager()

    results = manager.clean([source_1, source_2])

    assert len(results) == 1


def test_source_manager_removes_empty_sources():

    source = Source(
        id="1",
        title="Empty Source",
        url="https://example.com",
        source_type="article",
        content=None,
    )

    manager = SourceManager()

    results = manager.clean([source])

    assert len(results) == 0