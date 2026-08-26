import logging
from uuid import uuid4

from app.core.evidence_cache import EvidenceCache
from app.core.llm import LLMProvider
from app.models.schemas import (
    Claim,
    Evidence,
    EvidenceAnalysis,
    Source,
)


logger = logging.getLogger(__name__)


class EvidenceAgent:

    def __init__(
        self,
        llm: LLMProvider,
        cache: EvidenceCache | None = None,
    ):
        self.llm = llm
        self.cache = cache or EvidenceCache()

    def analyze(
        self,
        source: Source,
    ) -> EvidenceAnalysis:

        # -----------------------------------------------------
        # Validate source content
        # -----------------------------------------------------

        if not source.content:

            return EvidenceAnalysis(
                claims=[],
                evidence=[],
            )

        # -----------------------------------------------------
        # Check evidence cache
        # -----------------------------------------------------

        cached = self.cache.get(
            source.content
        )

        if cached is not None:

            logger.info(
                "Evidence cache hit: %s",
                source.title,
            )

            return cached

        logger.info(
            "Evidence cache miss: %s",
            source.title,
        )

        # -----------------------------------------------------
        # Build extraction prompt
        # -----------------------------------------------------

        prompt = f"""
You are an evidence extraction agent
inside an autonomous research system.

Analyze the following research source.

SOURCE TITLE:
{source.title}

SOURCE URL:
{source.url}

SOURCE CONTENT:
{source.content}

Extract:

1. The important factual claims made by the source.
2. The evidence directly supporting those claims.

Rules:

- Only extract information supported by the source.
- Do not invent facts.
- Do not add outside knowledge.
- Every claim MUST reference at least one evidence ID.
- Every evidence item MUST reference a valid claim ID.
- Evidence should be specific and directly support its claim.
- Assign a confidence score between 0 and 1.
- Assign evidence strength as weak, moderate, or strong.
- Include the approximate evidence location when possible.

Return JSON with exactly this structure:

{{
    "claims": [
        {{
            "id": "claim-1",
            "statement": "factual claim",
            "source_id": "{source.id}",
            "confidence": 0.0,
            "evidence_ids": [
                "evidence-1"
            ]
        }}
    ],
    "evidence": [
        {{
            "id": "evidence-1",
            "claim_id": "claim-1",
            "source_id": "{source.id}",
            "content": "supporting evidence",
            "strength": "strong",
            "location": "paragraph 4"
        }}
    ]
}}
"""

        # -----------------------------------------------------
        # Ask LLM
        # -----------------------------------------------------

        data = self.llm.generate_json(
            prompt,
            EvidenceAnalysis.model_json_schema(),
        )

        # -----------------------------------------------------
        # Parse claims
        # -----------------------------------------------------

        claims = []

        for item in data.get(
            "claims",
            [],
        ):

            claim_id = item.get(
                "id",
                str(uuid4()),
            )

            claims.append(
                Claim(
                    id=claim_id,
                    statement=item["statement"],
                    source_id=source.id,
                    confidence=float(
                        item.get(
                            "confidence",
                            0.0,
                        )
                    ),
                    evidence_ids=item.get(
                        "evidence_ids",
                        [],
                    ),
                )
            )

        # -----------------------------------------------------
        # Build valid claim ID set
        # -----------------------------------------------------

        claim_ids = {
            claim.id
            for claim in claims
        }

        # -----------------------------------------------------
        # Parse evidence
        # -----------------------------------------------------

        evidence = []

        for item in data.get(
            "evidence",
            [],
        ):

            claim_id = item.get(
                "claim_id"
            )

            # Ignore orphan evidence
            if claim_id not in claim_ids:
                continue

            evidence_id = item.get(
                "id",
                str(uuid4()),
            )

            evidence.append(
                Evidence(
                    id=evidence_id,
                    claim_id=claim_id,
                    source_id=source.id,
                    content=item["content"],
                    strength=item["strength"],
                    location=item.get(
                        "location"
                    ),
                )
            )

        # -----------------------------------------------------
        # Validate claim → evidence relationships
        # -----------------------------------------------------

        valid_evidence_ids = {
            item.id
            for item in evidence
        }

        for claim in claims:

            claim.evidence_ids = [
                evidence_id
                for evidence_id in claim.evidence_ids
                if evidence_id in valid_evidence_ids
            ]

        # -----------------------------------------------------
        # Remove claims without supporting evidence
        # -----------------------------------------------------

        supported_claims = [
            claim
            for claim in claims
            if claim.evidence_ids
        ]

        supported_claim_ids = {
            claim.id
            for claim in supported_claims
        }

        evidence = [
            item
            for item in evidence
            if item.claim_id in supported_claim_ids
        ]

        # -----------------------------------------------------
        # Build final analysis
        # -----------------------------------------------------

        result = EvidenceAnalysis(
            claims=supported_claims,
            evidence=evidence,
        )

        # -----------------------------------------------------
        # Save to evidence cache
        # -----------------------------------------------------

        self.cache.set(
            source.content,
            result,
        )

        return result