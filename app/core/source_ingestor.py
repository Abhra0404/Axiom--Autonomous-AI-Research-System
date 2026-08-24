import logging

import trafilatura

from app.core.source_cache import SourceCache
from app.models.schemas import Source


logger = logging.getLogger(__name__)


class SourceIngestor:

    def __init__(
        self,
        cache: SourceCache | None = None,
    ):
        self.cache = cache or SourceCache()

    def ingest(self, source: Source) -> Source | None:

        # -----------------------------------------------------
        # Check cache
        # -----------------------------------------------------

        cached = self.cache.get(
            str(source.url)
        )

        if cached is not None:
            logger.info(
                "Cache hit: %s",
                source.url,
            )

            return cached

        logger.info(
            "Cache miss: %s",
            source.url,
        )

        # -----------------------------------------------------
        # Download webpage
        # -----------------------------------------------------

        try:
            downloaded = trafilatura.fetch_url(
                str(source.url)
            )

        except Exception as error:
            logger.warning(
                "Failed to download %s: %s",
                source.url,
                error,
            )

            return None

        if not downloaded:
            logger.warning(
                "Empty response: %s",
                source.url,
            )

            return None

        # -----------------------------------------------------
        # Extract main content
        # -----------------------------------------------------

        try:
            content = trafilatura.extract(
                downloaded,
                include_links=True,
                include_tables=True,
            )

        except Exception as error:
            logger.warning(
                "Failed to extract %s: %s",
                source.url,
                error,
            )

            return None

        if not content:
            logger.warning(
                "No content extracted: %s",
                source.url,
            )

            return None

        # -----------------------------------------------------
        # Update source
        # -----------------------------------------------------

        source = source.model_copy(
            update={
                "content": content,
            }
        )

        # -----------------------------------------------------
        # Save to cache
        # -----------------------------------------------------

        self.cache.set(source)

        return source