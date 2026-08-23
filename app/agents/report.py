from app.core.llm import LLMProvider
from app.models.schemas import (
    EvidenceAnalysis,
    ResearchPlan,
    ResearchReport,
    Source,
    Critique,
)


class ReportAgent:

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def generate(
        self,
        plan: ResearchPlan,
        sources: list[Source],
        analyses: list[EvidenceAnalysis],
        critique: Critique,
    ) -> ResearchReport:

        context = self._build_context(
            sources,
            analyses,
        )

        prompt = f"""
You are the final report generation agent
in an autonomous research system.

Create a rigorous research report based ONLY
on the research evidence provided below.

RESEARCH QUESTION:
{plan.question}

OBJECTIVES:
{plan.objectives}

SUB-QUESTIONS:
{plan.sub_questions}

RESEARCH EVIDENCE:
{context}

CRITIQUE:

Sufficient:
{critique.sufficient}

Overall confidence:
{critique.overall_confidence}

Strengths:
{critique.strengths}

Weaknesses:
{critique.weaknesses}

Missing information:
{critique.missing_information}

Requirements:

- Do not invent facts.
- Do not introduce outside information.
- Clearly distinguish evidence from interpretation.
- Mention conflicting evidence when present.
- Be scientifically cautious.
- Do not overstate conclusions.
- The conclusion must directly answer the research question.
- Preserve uncertainty where evidence is weak.

Return structured data matching the provided schema.
"""

        data = self.llm.generate_json(
            prompt,
            ResearchReport.model_json_schema(),
        )

        return ResearchReport.model_validate(data)

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