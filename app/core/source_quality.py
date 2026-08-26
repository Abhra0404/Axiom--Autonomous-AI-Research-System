from urllib.parse import urlparse

from app.models.schemas import Source


class SourceQualityScorer:

    TYPE_SCORES = {
        "paper": 1.00,
        "documentation": 0.90,
        "report": 0.85,
        "dataset": 0.80,
        "article": 0.45,
        "other": 0.30,
    }

    DOMAIN_SCORES = {
        "arxiv.org": 1.00,
        "nature.com": 1.00,
        "science.org": 1.00,
        "acm.org": 0.95,
        "ieee.org": 0.95,
        "springer.com": 0.95,
        "nih.gov": 0.95,
        "ncbi.nlm.nih.gov": 0.95,
        "github.com": 0.80,
        "readthedocs.io": 0.80,
    }

    def score(
        self,
        source: Source,
    ) -> float:

        # -----------------------------------------------------
        # Domain-based quality takes priority
        # -----------------------------------------------------

        domain_score = self._domain_score(
            str(source.url)
        )

        if domain_score is not None:
            return domain_score

        # -----------------------------------------------------
        # Fall back to source type
        # -----------------------------------------------------

        source_type = (
            source.source_type
            .lower()
            .strip()
        )

        return self.TYPE_SCORES.get(
            source_type,
            0.30,
        )

    def apply(
        self,
        source: Source,
    ) -> Source:

        return source.model_copy(
            update={
                "quality_score": self.score(
                    source
                )
            }
        )

    def _domain_score(
        self,
        url: str,
    ) -> float | None:

        try:
            hostname = urlparse(
                url
            ).hostname

        except Exception:
            return None

        if not hostname:
            return None

        hostname = hostname.lower()

        # Exact domain
        if hostname in self.DOMAIN_SCORES:
            return self.DOMAIN_SCORES[
                hostname
            ]

        # Subdomain
        for domain, score in self.DOMAIN_SCORES.items():

            if hostname.endswith(
                f".{domain}"
            ):
                return score

        # Government domains
        if hostname.endswith(".gov"):
            return 0.90

        # Educational domains
        if hostname.endswith(".edu"):
            return 0.85

        return None