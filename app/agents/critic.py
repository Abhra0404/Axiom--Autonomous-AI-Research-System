import json
import logging

from app.core.llm import LLMProvider
from app.models.schemas import (
    ClaimRelationship,
    Critique,
)


logger = logging.getLogger(__name__)


class CriticAgent:

    def __init__(
        self,
        llm: LLMProvider,
    ):
        self.llm = llm

    def critique(
        self,
        plan,
        sources,
        analyses,
        relationships: list[ClaimRelationship] | None = None,
    ) -> Critique:

        relationships = relationships or []

        # -----------------------------------------------------
        # Collect contradictions
        # -----------------------------------------------------

        contradictions = [
            relationship
            for relationship in relationships
            if relationship.relationship
            == "contradicts"
        ]

        # -----------------------------------------------------
        # Collect claims
        # -----------------------------------------------------

        claims = [
            claim
            for analysis in analyses
            for claim in analysis.claims
        ]

        # -----------------------------------------------------
        # Format claims
        # -----------------------------------------------------

        claim_text = "\n".join(
            (
                f"{claim.id}: "
                f"{claim.statement} "
                f"(confidence={claim.confidence:.2f})"
            )
            for claim in claims
        )

        # -----------------------------------------------------
        # Format relationships
        # -----------------------------------------------------

        relationship_text = "\n".join(
            (
                f"{relationship.claim_a} "
                f"--{relationship.relationship}--> "
                f"{relationship.claim_b} "
                f"(confidence="
                f"{relationship.confidence:.2f})"
            )
            for relationship in relationships
        )

        if not relationship_text:
            relationship_text = "No claim relationships detected."

        # -----------------------------------------------------
        # Format sources
        # -----------------------------------------------------

        source_text = "\n".join(
            (
                f"{source.id}: "
                f"{source.title} "
                f"({source.url}) "
                f"quality={source.quality_score:.2f}"
            )
            for source in sources
        )

        # -----------------------------------------------------
        # Format research plan
        # -----------------------------------------------------

        objectives = getattr(
            plan,
            "objectives",
            [],
        )

        sub_questions = getattr(
            plan,
            "sub_questions",
            [],
        )

        question = getattr(
            plan,
            "question",
            "",
        )

        # -----------------------------------------------------
        # Build prompt
        # -----------------------------------------------------

        prompt = f"""
You are the critic agent in Axiom,
an autonomous research system.

Your job is to determine whether the current research
contains enough reliable evidence to answer the research
question.

RESEARCH QUESTION:
{question}

OBJECTIVES:
{json.dumps(objectives, indent=2)}

SUB-QUESTIONS:
{json.dumps(sub_questions, indent=2)}

SOURCES:
{source_text}

CLAIMS:
{claim_text}

CLAIM RELATIONSHIPS:
{relationship_text}

CONTRADICTIONS DETECTED:
{len(contradictions)}

Evaluate:

1. Whether the evidence is sufficient.
2. Overall confidence in the research.
3. Strengths of the current research.
4. Weaknesses.
5. Missing information.
6. Follow-up questions that should be researched.

Important rules:

- Do not assume evidence is sufficient simply because
  multiple sources exist.
- High-confidence contradictions between credible sources
  should generally make the research insufficient.
- Duplicate claims do not count as independent evidence.
- Supporting claims increase confidence.
- Consider source quality when evaluating evidence.
- Identify important gaps.
- Do not invent facts.

Return JSON:

{{
    "sufficient": true,
    "overall_confidence": 0.0,
    "strengths": [
        "..."
    ],
    "weaknesses": [
        "..."
    ],
    "missing_information": [
        "..."
    ],
    "follow_up_questions": [
        "..."
    ]
}}
"""

        # -----------------------------------------------------
        # Ask LLM
        # -----------------------------------------------------

        data = self.llm.generate_json(
            prompt,
            Critique.model_json_schema(),
        )

        # -----------------------------------------------------
        # Validate LLM output
        # -----------------------------------------------------

        critique = Critique.model_validate(
            data
        )

        # -----------------------------------------------------
        # Deterministic contradiction override
        # -----------------------------------------------------

        strong_contradictions = [
            relationship
            for relationship in contradictions
            if relationship.confidence >= 0.80
        ]

        if strong_contradictions:

            critique.sufficient = False

            message = (
                "Conflicting evidence requires "
                "further research."
            )

            if message not in critique.weaknesses:
                critique.weaknesses.append(
                    message
                )

            logger.info(
                "Critic rejected research due to "
                "%d strong contradiction(s).",
                len(strong_contradictions),
            )

        # -----------------------------------------------------
        # Return critique
        # -----------------------------------------------------

        return critique