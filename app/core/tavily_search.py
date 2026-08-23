import os

from dotenv import load_dotenv
from tavily import TavilyClient

from app.core.search import SearchProvider
from app.models.schemas import Source
from hashlib import sha256


load_dotenv()


class TavilySearchProvider(SearchProvider):

    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise ValueError("TAVILY_API_KEY is not configured")

        self.client = TavilyClient(api_key=api_key)

    def search(self, query: str) -> list[Source]:
        response = self.client.search(
            query=query,
            search_depth="advanced",
            max_results=2,
        )

        sources = []

        for index, result in enumerate(response.get("results", [])):
            sources.append(
                Source(
                    id=sha256(result["url"].encode()).hexdigest()[:16],
                    title=result.get("title", "Untitled"),
                    url=result["url"],
                    source_type="article",
                )
            )

        return sources