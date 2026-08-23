from app.models.schemas import Source

import trafilatura


class SourceIngestor:

    def ingest(self, source: Source) -> Source:
        content = trafilatura.fetch_url(str(source.url))

        if not content:
            return source

        return source.model_copy(
            update={
                "content": content,
            }
        )