import re

from app.models.schemas import Source


class SourceRanker:

    def select(
        self,
        sources: list[Source],
        top_k: int = 3,
    ) -> list[Source]:

        return sources[:top_k]

    def rank(
        self,
        sources: list[Source],
        query: str,
    ) -> list[Source]:

        query_terms = self._tokenize(query)

        ranked_sources = []

        for source in sources:

            text = " ".join(
                [
                    source.title,
                    source.content or "",
                ]
            ).lower()

            score = self._calculate_score(
                text,
                query_terms,
            )

            ranked_sources.append(
                source.model_copy(
                    update={
                        "relevance_score": score,
                    }
                )
            )

        return sorted(
            ranked_sources,
            key=lambda source: source.relevance_score,
            reverse=True,
        )

    @staticmethod
    def _tokenize(text: str) -> set[str]:

        words = re.findall(
            r"\b[a-zA-Z]{3,}\b",
            text.lower(),
        )

        stop_words = {
            "the",
            "and",
            "for",
            "with",
            "does",
            "what",
            "how",
            "are",
            "this",
            "that",
            "from",
            "into",
            "about",
        }

        return {
            word
            for word in words
            if word not in stop_words
        }

    @staticmethod
    def _calculate_score(
        text: str,
        query_terms: set[str],
    ) -> float:

        if not query_terms:
            return 0.0

        matched_terms = sum(
            1
            for term in query_terms
            if term in text
        )

        return min(
            matched_terms / len(query_terms),
            1.0,
        )