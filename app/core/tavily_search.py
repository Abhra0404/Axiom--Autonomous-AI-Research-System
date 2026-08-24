import os
from hashlib import sha256

from dotenv import load_dotenv
from tavily import TavilyClient

from app.core.search import SearchProvider
from app.models.schemas import Source


load_dotenv()


class TavilySearchProvider(SearchProvider):

    def __init__(self, client=None):
        if client is not None:
            self.client = client
            return

        api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise ValueError(
                "TAVILY_API_KEY is not configured"
            )

        self.client = TavilyClient(
            api_key=api_key
        )

    def search(self, query: str) -> list[Source]:

        response = self.client.search(
            query=query,
            search_depth="advanced",
            max_results=2,
        )

        sources = []

        for result in response.get(
            "results",
            [],
        ):
            url = result["url"]

            sources.append(
                Source(
                    id=sha256(
                        url.encode()
                    ).hexdigest()[:16],
                    title=result.get(
                        "title",
                        "Untitled",
                    ),
                    url=url,
                    source_type="article",
                )
            )

        return sources