from app.models.schemas import Source


class SourceManager:

    def clean(
        self,
        sources: list[Source | None],
    ) -> list[Source]:

        cleaned: list[Source] = []

        seen_ids: set[str] = set()
        seen_urls: set[str] = set()

        for source in sources:

            if source is None:
                continue

            if not source.content:
                continue

            source_id = str(source.id)

            # Normalize URL:
            # https://example.com/paper
            # https://example.com/paper/
            # should be treated as the same URL.
            source_url = str(source.url).rstrip("/")

            if source_id in seen_ids:
                continue

            if source_url in seen_urls:
                continue

            seen_ids.add(source_id)
            seen_urls.add(source_url)

            cleaned.append(source)

        return cleaned