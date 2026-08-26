import logging

from app.core.evidence_cache import EvidenceCache
from app.core.llm import LLMProvider
from app.models.schemas import EvidenceAnalysis, Source


logger = logging.getLogger(__name__)


class EvidenceAgent:

    def __init__(
        self,
        llm: LLMProvider,
        cache: EvidenceCache | None = None,
    ):
        self.llm = llm
        self.cache = cache

    def analyze(
        self,
        source: Source,
    ) -> EvidenceAnalysis | None:

        # -----------------------------------------------------
        # Cache lookup
        # -----------------------------------------------------

        if self.cache is not None:

            cached = self.cache.get(
                source.id
            )

            if cached is not None:

                # Cached data may already be a
                # Pydantic model or a dictionary.
                if isinstance(
                    cached,
                    EvidenceAnalysis,
                ):
                    return cached

                return EvidenceAnalysis.model_validate(
                    {
                        **cached,
                        "source_id": str(
                            source.id
                        ),
                    }
                )

        # -----------------------------------------------------
        # Validate source content
        # -----------------------------------------------------

        if not source.content:

            logger.warning(
                "No content available for source: %s",
                source.url,
            )

            return None

        # -----------------------------------------------------
        # Research prompt
        # -----------------------------------------------------

        prompt = f"""
You are an evidence extraction agent
in an autonomous research system.

Analyze the following research source.

SOURCE TITLE:
{source.title}

SOURCE URL:
{source.url}

SOURCE CONTENT:
{source.content}

Extract:

1. Claims explicitly supported by the source.
2. Evidence supporting those claims.

Rules:

- Only extract claims that are supported by
  the provided source.
- Do not invent information.
- Do not add outside knowledge.
- Keep claims concise and factual.
- Each claim must have a unique ID.
- Each evidence item must reference a claim ID.
- Evidence should quote or closely summarize
  the relevant source content.
- Assign a confidence score between 0 and 1.

Return JSON in this structure:

{{
    "claims": [
        {{
            "id": "claim-1",
            "statement": "...",
            "source_id": "{source.id}",
            "confidence": 0.0
        }}
    ],
    "evidence": [
        {{
            "id": "evidence-1",
            "claim_id": "claim-1",
            "source_id": "{source.id}",
            "content": "...",
            "strength": "strong"
        }}
    ]
}}

The source_id in the final Python object will be
assigned by the system. Do not rely on the model
to provide it correctly.
"""

        # -----------------------------------------------------
        # LLM call
        # -----------------------------------------------------

        data = self.llm.generate_json(
            prompt,
            EvidenceAnalysis.model_json_schema(),
        )

        if not data:

            logger.warning(
                "Empty evidence response for source: %s",
                source.url,
            )

            return None

        # -----------------------------------------------------
        # Inject authoritative source ID
        # -----------------------------------------------------

        data = {
            **data,
            "source_id": str(
                source.id
            ),
        }

        # -----------------------------------------------------
        # Validate structured result
        # -----------------------------------------------------

        analysis = EvidenceAnalysis.model_validate(
            data
        )

        # -----------------------------------------------------
        # Cache result
        # -----------------------------------------------------

        if self.cache is not None:

            self.cache.set(
                source.id,
                analysis,
            )

        return analysis