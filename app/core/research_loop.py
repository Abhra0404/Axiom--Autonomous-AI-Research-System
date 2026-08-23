from dataclasses import dataclass

from app.agents.critic import CriticAgent
from app.agents.evidence import EvidenceAgent
from app.agents.planner import Planner
from app.agents.researcher import Researcher
from app.core.source_ranker import SourceRanker
from app.models.schemas import (
    Critique,
    EvidenceAnalysis,
    ResearchPlan,
    Source,
)


@dataclass
class ResearchResult:
    plan: ResearchPlan
    sources: list[Source]
    analyses: list[EvidenceAnalysis]
    critique: Critique
    iterations: int


class ResearchLoop:

    def __init__(
        self,
        planner: Planner,
        researcher: Researcher,
        evidence_agent: EvidenceAgent,
        critic: CriticAgent,
        source_ranker: SourceRanker,
        max_iterations: int = 3,
    ):
        self.planner = planner
        self.researcher = researcher
        self.evidence_agent = evidence_agent
        self.critic = critic
        self.source_ranker = source_ranker
        self.max_iterations = max_iterations

    def run(
        self,
        plan: ResearchPlan,
    ) -> ResearchResult:

        all_sources: list[Source] = []
        all_analyses: list[EvidenceAnalysis] = []

        current_plan = plan
        iteration = 0
        critique = None

        while iteration < self.max_iterations:

            iteration += 1

            print(
                f"\n{'=' * 70}"
            )
            print(
                f"RESEARCH ITERATION {iteration}"
            )
            print(
                f"{'=' * 70}"
            )

            # ---------------------------------------------
            # Search
            # ---------------------------------------------

            sources = self.researcher.search(
                current_plan
            )

            # ---------------------------------------------
            # Rank
            # ---------------------------------------------

            sources = self.source_ranker.rank(
                sources,
                current_plan.question,
            )

            sources = self.source_ranker.select(
                sources,
                top_k=3,
            )

            # ---------------------------------------------
            # Deduplicate across iterations
            # ---------------------------------------------

            existing_urls = {
                str(source.url)
                for source in all_sources
            }

            sources = [
                source
                for source in sources
                if str(source.url)
                not in existing_urls
            ]

            if not sources:
                print(
                    "No new sources found."
                )
                break

            all_sources.extend(sources)

            print(
                f"New sources: {len(sources)}"
            )

            # ---------------------------------------------
            # Evidence extraction
            # ---------------------------------------------

            for source in sources:

                try:

                    analysis = (
                        self.evidence_agent.analyze(
                            source
                        )
                    )

                    all_analyses.append(
                        analysis
                    )

                    print(
                        f"Analyzed: "
                        f"{source.title}"
                    )

                except Exception as error:

                    print(
                        f"Failed: "
                        f"{source.title}"
                    )

                    print(
                        f"Error: {error}"
                    )

            # ---------------------------------------------
            # Critique
            # ---------------------------------------------

            critique = self.critic.critique(
                current_plan,
                all_sources,
                all_analyses,
            )

            print(
                f"\nSufficient: "
                f"{critique.sufficient}"
            )

            print(
                f"Confidence: "
                f"{critique.overall_confidence:.2f}"
            )

            # ---------------------------------------------
            # Stop condition
            # ---------------------------------------------

            if critique.sufficient:

                print(
                    "\nResearch is sufficient."
                )

                break

            # ---------------------------------------------
            # Generate next research plan
            # ---------------------------------------------

            if not critique.follow_up_questions:

                print(
                    "\nNo follow-up questions."
                )

                break

            current_plan = self._create_follow_up_plan(
                current_plan,
                critique,
            )

        if critique is None:

            raise RuntimeError(
                "Research loop produced no critique."
            )

        return ResearchResult(
            plan=plan,
            sources=all_sources,
            analyses=all_analyses,
            critique=critique,
            iterations=iteration,
        )

    @staticmethod
    def _create_follow_up_plan(
        plan: ResearchPlan,
        critique: Critique,
    ) -> ResearchPlan:

        return plan.model_copy(
            update={
                "sub_questions": (
                    critique.follow_up_questions
                ),
                "search_queries": (
                    critique.follow_up_questions
                ),
            }
        )