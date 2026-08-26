from app.core.search import SearchProvider
from app.core.source_ingestor import SourceIngestor
from app.core.source_manager import SourceManager
from app.models.schemas import ResearchPlan, Source


class Researcher:

    def __init__(
        self,
        search_provider: SearchProvider,
        source_ingestor: SourceIngestor,
        source_manager: SourceManager,
    ):
        self.search_provider = search_provider
        self.source_ingestor = source_ingestor
        self.source_manager = source_manager

    def search(
        self,
        plan: ResearchPlan,
    ) -> list[Source]:

        sources: list[Source] = []

        for query in plan.search_queries:

            results = self.search_provider.search(
                query
            )

            for source in results:

                if source is None:
                    continue

                source.search_query = query

                ingested = (
                    self.source_ingestor.ingest(
                        source
                    )
                )

                if ingested is None:
                    continue

                sources.append(
                    ingested
                )

        if not sources:
            return []

        return self.source_manager.clean(
            sources
        )