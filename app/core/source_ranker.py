import re

from app.core.source_quality import SourceQualityScorer
from app.models.schemas import Source


class SourceRanker:

    def __init__(
        self,
        quality_scorer: SourceQualityScorer | None = None,
    ):
        self.quality_scorer = (
            quality_scorer
            or SourceQualityScorer()
        )

    def rank(
        self,
        sources: list[Source],
        query: str,
    ) -> list[Source]:

        query_terms = self._tokenize(query)

        ranked_sources = []

        for source in sources:

            relevance_score = self._calculate_score(
                " ".join(
                    [
                        source.title,
                        source.content or "",
                    ]
                ).lower(),
                query_terms,
            )

            source = source.model_copy(
                update={
                    "relevance_score": relevance_score,
                }
            )

            source = self.quality_scorer.apply(
                source
            )

            final_score = (
                0.70 * source.relevance_score
                + 0.30 * source.quality_score
            )

            ranked_sources.append(
                (
                    final_score,
                    source,
                )
            )

        ranked_sources.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            source
            for _, source in ranked_sources
        ]

    @staticmethod
    def select(
        sources: list[Source],
        top_k: int = 3,
    ) -> list[Source]:

        return sources[:top_k]

    @staticmethod
    def _tokenize(
        text: str,
    ) -> set[str]:

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