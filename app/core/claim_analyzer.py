from app.core.llm import LLMProvider
from app.models.schemas import (
    Claim,
    ClaimRelationship,
)


class ClaimAnalyzer:

    def __init__(
        self,
        llm: LLMProvider,
    ):
        self.llm = llm

    def analyze(
        self,
        claims: list[Claim],
    ) -> list[ClaimRelationship]:

        if len(claims) < 2:
            return []

        valid_claim_ids = {
            claim.id
            for claim in claims
        }

        relationships: list[
            ClaimRelationship
        ] = []

        # =====================================================
        # 1. LLM relationship analysis
        # =====================================================

        claim_text = "\n".join(
            f"{claim.id}: {claim.statement}"
            for claim in claims
        )

        prompt = f"""
You are a research claim analysis agent.

Analyze the following claims and identify
relationships between them.

CLAIMS:

{claim_text}

Possible relationship types:

- duplicate
- supports
- contradicts
- independent

Rules:

- Compare claims carefully.
- "contradicts" means the claims make incompatible
  assertions about the same proposition.
- "duplicate" means the claims express substantially
  the same conclusion using different wording.
- "supports" means one claim provides evidence for
  or strengthens another.
- Do not mark unrelated claims as contradictory.
- Only use the claim IDs provided.
- Do not invent claims.
- Return only meaningful relationships.
- Prefer high-confidence relationships.

Return JSON:

{{
    "relationships": [
        {{
            "claim_a": "claim-1",
            "claim_b": "claim-2",
            "relationship": "contradicts",
            "confidence": 0.92
        }}
    ]
}}
"""

        result = self.llm.generate_json(
            prompt,
            {
                "type": "object",
                "properties": {
                    "relationships": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "claim_a": {
                                    "type": "string"
                                },
                                "claim_b": {
                                    "type": "string"
                                },
                                "relationship": {
                                    "type": "string",
                                    "enum": [
                                        "duplicate",
                                        "supports",
                                        "contradicts",
                                        "independent",
                                    ],
                                },
                                "confidence": {
                                    "type": "number",
                                },
                            },
                            "required": [
                                "claim_a",
                                "claim_b",
                                "relationship",
                                "confidence",
                            ],
                        },
                    }
                },
                "required": [
                    "relationships"
                ],
            },
        )

        for relationship in result.get(
            "relationships",
            [],
        ):

            claim_a = relationship.get(
                "claim_a"
            )

            claim_b = relationship.get(
                "claim_b"
            )

            relationship_type = relationship.get(
                "relationship"
            )

            if (
                claim_a not in valid_claim_ids
                or claim_b not in valid_claim_ids
                or claim_a == claim_b
            ):
                continue

            if relationship_type == "independent":
                continue

            relationships.append(
                ClaimRelationship(
                    claim_a=claim_a,
                    claim_b=claim_b,
                    relationship=relationship_type,
                    confidence=float(
                        relationship.get(
                            "confidence",
                            0.0,
                        )
                    ),
                )
            )

        # =====================================================
        # 2. Deterministic contradiction detection
        # =====================================================

        existing_pairs = {
            frozenset(
                (
                    relationship.claim_a,
                    relationship.claim_b,
                )
            )
            for relationship in relationships
        }

        contradiction_pairs = []

        contradiction_phrases = [
            (
                "does not",
                "does",
            ),
            (
                "doesn't",
                "does",
            ),
            (
                "cannot",
                "can",
            ),
            (
                "can't",
                "can",
            ),
            (
                "no",
                "yes",
            ),
            (
                "not reduce",
                "reduce",
            ),
            (
                "not improve",
                "improve",
            ),
            (
                "not increase",
                "increase",
            ),
            (
                "not decrease",
                "decrease",
            ),
        ]

        for index, claim_a in enumerate(
            claims
        ):

            text_a = (
                claim_a.statement.lower()
            )

            for claim_b in claims[
                index + 1:
            ]:

                pair = frozenset(
                    (
                        claim_a.id,
                        claim_b.id,
                    )
                )

                if pair in existing_pairs:
                    continue

                text_b = (
                    claim_b.statement.lower()
                )

                for positive, negative in (
                    contradiction_phrases
                ):

                    if (
                        positive in text_a
                        and negative in text_b
                    ) or (
                        positive in text_b
                        and negative in text_a
                    ):

                        contradiction_pairs.append(
                            (
                                claim_a,
                                claim_b,
                            )
                        )

                        break

        for claim_a, claim_b in (
            contradiction_pairs
        ):

            relationships.append(
                ClaimRelationship(
                    claim_a=claim_a.id,
                    claim_b=claim_b.id,
                    relationship="contradicts",
                    confidence=0.85,
                )
            )

        # =====================================================
        # 3. Deterministic duplicate detection
        # =====================================================

        existing_pairs = {
            frozenset(
                (
                    relationship.claim_a,
                    relationship.claim_b,
                )
            )
            for relationship in relationships
        }

        # Very lightweight normalization.
        # We intentionally do NOT try to replace
        # semantic similarity with string matching.
        def normalize(text: str) -> set[str]:

            stop_words = {
                "the",
                "a",
                "an",
                "is",
                "are",
                "of",
                "to",
                "and",
                "in",
                "for",
                "that",
                "this",
                "can",
                "may",
            }

            words = (
                text.lower()
                .replace(".", "")
                .replace(",", "")
                .split()
            )

            return {
                word
                for word in words
                if word not in stop_words
            }

        for index, claim_a in enumerate(
            claims
        ):

            words_a = normalize(
                claim_a.statement
            )

            for claim_b in claims[
                index + 1:
            ]:

                pair = frozenset(
                    (
                        claim_a.id,
                        claim_b.id,
                    )
                )

                if pair in existing_pairs:
                    continue

                words_b = normalize(
                    claim_b.statement
                )

                if not words_a or not words_b:
                    continue

                overlap = (
                    len(words_a & words_b)
                    / len(words_a | words_b)
                )

                if overlap >= 0.80:

                    relationships.append(
                        ClaimRelationship(
                            claim_a=claim_a.id,
                            claim_b=claim_b.id,
                            relationship="duplicate",
                            confidence=round(
                                overlap,
                                2,
                            ),
                        )
                    )

        return relationships