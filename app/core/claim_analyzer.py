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

        claim_text = "\n".join(
            f"{claim.id}: {claim.statement}"
            for claim in claims
        )

        prompt = f"""
You are a research claim analysis agent.

Analyze the following claims.

CLAIMS:

{claim_text}

Identify relationships between claims.

Possible relationship types:

- "duplicate"
- "supports"
- "contradicts"
- "independent"

Rules:

- Only identify relationships supported by the wording.
- Do not invent claims.
- Do not assume two claims contradict each other simply
  because they discuss different results.
- Return only valid claim IDs.

Return JSON:

{{
    "relationships": [
        {{
            "claim_a": "claim-1",
            "claim_b": "claim-2",
            "relationship": "contradicts",
            "confidence": 0.0
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

        valid_claim_ids = {
            claim.id
            for claim in claims
        }

        relationships = []

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

            if (
                claim_a not in valid_claim_ids
                or claim_b not in valid_claim_ids
                or claim_a == claim_b
            ):
                continue

            relationships.append(
                ClaimRelationship(
                    claim_a=claim_a,
                    claim_b=claim_b,
                    relationship=relationship[
                        "relationship"
                    ],
                    confidence=float(
                        relationship.get(
                            "confidence",
                            0.0,
                        )
                    ),
                )
            )

        return relationships