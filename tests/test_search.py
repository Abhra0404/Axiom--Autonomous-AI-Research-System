from app.core.tavily_search import TavilySearchProvider
from unittest.mock import MagicMock

provider = MagicMock()

results = provider.search(
    "retrieval augmented generation hallucinations LLM research"
)

for result in results:
    print(f"\nTitle: {result.title}")
    print(f"URL: {result.url}")