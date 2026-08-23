from app.core.llm import LLMProvider
from app.models.schemas import (
    Critique,
    EvidenceAnalysis,
    ResearchPlan,
    Source,
)


class CriticAgent:

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def critique(
        self,
        plan: ResearchPlan,
        sources: list[Source],
        analyses: list[EvidenceAnalysis],
    ) -> Critique:

        research_context = self._build_context(
            sources,
            analyses,
        )

        prompt = f"""
You are the critical evaluation agent in an
autonomous research system.

Your task is to evaluate whether the collected
evidence is sufficient to answer the research
question.

RESEARCH QUESTION:
{plan.question}

OBJECTIVES:
{plan.objectives}

SUB-QUESTIONS:
{plan.sub_questions}

RESEARCH EVIDENCE:
{research_context}

Evaluate:

1. Whether the evidence is sufficient.
2. Overall confidence in the findings.
3. Strengths of the evidence.
4. Weaknesses and limitations.
5. Missing information.
6. Follow-up questions that should be researched.

Be skeptical.

Do not assume that a claim is true merely because
a source states it.

Look for:
- conflicting findings
- weak evidence
- unsupported claims
- missing perspectives
- insufficient sample sizes
- outdated evidence
- gaps in the research

Return only structured data matching the provided schema.
"""

        data = self.llm.generate_json(
            prompt,
            Critique.model_json_schema(),
        )

        return Critique.model_validate(data)

    @staticmethod
    def _build_context(
        sources: list[Source],
        analyses: list[EvidenceAnalysis],
    ) -> str:

        sections = []

        for source, analysis in zip(
            sources,
            analyses,
        ):

            section = [
                f"SOURCE: {source.title}",
                f"URL: {source.url}",
                "",
                "CLAIMS:",
            ]

            for claim in analysis.claims:
                section.append(
                    f"- {claim.statement} "
                    f"(confidence={claim.confidence:.2f})"
                )

            section.append("")
            section.append("EVIDENCE:")

            for evidence in analysis.evidence:
                section.append(
                    f"- {evidence.content} "
                    f"(strength={evidence.strength})"
                )

            sections.append(
                "\n".join(section)
            )

        return "\n\n".join(sections)