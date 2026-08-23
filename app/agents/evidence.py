from uuid import uuid4

from app.core.llm import LLMProvider
from app.models.schemas import (
    Claim,
    Evidence,
    EvidenceAnalysis,
    Source,
)


class EvidenceAgent:

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def analyze(self, source: Source) -> EvidenceAnalysis:

        if not source.content:
            return EvidenceAnalysis(
                claims=[],
                evidence=[],
            )

        prompt = f"""
You are an evidence extraction agent for a research system.

Analyze the following research source.

SOURCE ID:
{source.id}

SOURCE TITLE:
{source.title}

SOURCE CONTENT:
{source.content}

Extract the important factual claims supported by this source.

For each claim:

1. Write a concise factual statement.
2. Give a confidence score between 0 and 1.
3. Provide the supporting evidence.
4. Classify evidence strength as weak, moderate, or strong.

Rules:

- Only use information explicitly supported by the source.
- Do not invent facts.
- Do not use outside knowledge.
- Keep claims concise.
- Evidence must directly support the claim.

Return ONLY valid JSON in this format:

{{
    "claims": [
        {{
            "id": "claim-id",
            "statement": "factual claim",
            "source_id": "{source.id}",
            "confidence": 0.0
        }}
    ],
    "evidence": [
        {{
            "id": "evidence-id",
            "claim_id": "claim-id",
            "source_id": "{source.id}",
            "content": "supporting evidence",
            "strength": "weak"
        }}
    ]
}}
"""

        data = self.llm.generate_json(
            prompt,
            EvidenceAnalysis.model_json_schema(),
        )

        # Validate and normalize IDs
        claims = []

        for claim in data.get("claims", []):
            claims.append(
                Claim(
                    id=claim.get("id", str(uuid4())),
                    statement=claim["statement"],
                    source_id=source.id,
                    confidence=claim["confidence"],
                )
            )

        evidence = []

        for item in data.get("evidence", []):
            evidence.append(
                Evidence(
                    id=item.get("id", str(uuid4())),
                    claim_id=item["claim_id"],
                    source_id=source.id,
                    content=item["content"],
                    strength=item["strength"],
                )
            )

        return EvidenceAnalysis(
            claims=claims,
            evidence=evidence,
        )