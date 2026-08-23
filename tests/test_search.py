from app.core.tavily_search import TavilySearchProvider


provider = TavilySearchProvider()

results = provider.search(
    "retrieval augmented generation hallucinations LLM research"
)

for result in results:
    print(f"\nTitle: {result.title}")
    print(f"URL: {result.url}")