from app.models.schemas import Source
from app.core.search import SearchProvider


class MockSearchProvider(SearchProvider):

    def search(self, query: str) -> list[Source]:
        return [
            Source(
                id="mock-001",
                title=f"Research results for {query}",
                url="https://example.com/research",
                source_type="article",
                authors=["Axiom"],
            )
        ]