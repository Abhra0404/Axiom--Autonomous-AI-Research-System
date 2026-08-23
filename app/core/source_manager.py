from urllib.parse import urlparse

from app.models.schemas import Source


class SourceManager:

    def clean(self, sources: list[Source]) -> list[Source]:
        unique_sources: dict[str, Source] = {}

        for source in sources:
            if not source.content:
                continue

            normalized_url = self._normalize_url(str(source.url))

            if normalized_url not in unique_sources:
                unique_sources[normalized_url] = source

        return list(unique_sources.values())

    @staticmethod
    def _normalize_url(url: str) -> str:
        parsed = urlparse(url)

        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")