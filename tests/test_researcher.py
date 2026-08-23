from unittest.mock import MagicMock

from app.agents.planner import Planner
from app.agents.researcher import Researcher
from app.core.mock_search import MockSearchProvider
from app.core.source_ingestor import SourceIngestor
from app.core.source_manager import SourceManager
from app.models.schemas import ResearchRequest


def test_researcher_returns_sources():
    request = ResearchRequest(
        topic="Does RAG reduce hallucinations in LLMs?",
        depth="deep",
    )

    planner = Planner()
    plan = planner.create_plan(request)

    ingestor = MagicMock(spec=SourceIngestor)

    def mock_ingest(source):
        return source.model_copy(
            update={
                "content": "This is mock research content."
            }
        )

    ingestor.ingest.side_effect = mock_ingest

    researcher = Researcher(
        MockSearchProvider(),
        ingestor,
        SourceManager(),
    )

    sources = researcher.search(plan)

    assert len(sources) > 0
    assert sources[0].title
    assert sources[0].url
    assert sources[0].content == "This is mock research content."