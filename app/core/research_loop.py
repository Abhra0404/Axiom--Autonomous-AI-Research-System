from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from app.models.schemas import (
    ClaimRelationship,
    Critique,
    EvidenceAnalysis,
    ResearchPlan,
    Source,
)
from app.models.state import ResearchState
from app.models.events import ResearchEvent
from app.core.event_logger import ResearchEventLogger


@dataclass
class ResearchResult:
    plan: ResearchPlan
    sources: list[Source]
    analyses: list[EvidenceAnalysis]
    relationships: list[ClaimRelationship]
    critique: Critique
    iterations: int
    state: ResearchState
    events: list[ResearchEvent]


class ResearchLoop:

    def __init__(
        self,
        planner,
        researcher,
        source_ranker,
        evidence_agent,
        critic,
        claim_analyzer,
        event_logger: ResearchEventLogger | None = None,
        max_iterations: int = 3,
    ):
        self.planner = planner
        self.researcher = researcher
        self.source_ranker = source_ranker
        self.evidence_agent = evidence_agent
        self.critic = critic
        self.claim_analyzer = claim_analyzer
        self.event_logger = (
            event_logger
            or ResearchEventLogger()
        )
        self.max_iterations = max_iterations

    def run(
        self,
        plan: ResearchPlan,
    ) -> ResearchResult:

        # -----------------------------------------------------
        # Initialize state
        # -----------------------------------------------------

        state = ResearchState(
            run_id=uuid4(),
            status="running",
            started_at=datetime.now(
                timezone.utc
            ),
        )

        self.event_logger.emit(
            event="research_started",
            iteration=0,
        )

        # -----------------------------------------------------
        # Research collections
        # -----------------------------------------------------

        all_sources: list[Source] = []

        all_analyses: list[
            EvidenceAnalysis
        ] = []

        all_relationships: list[
            ClaimRelationship
        ] = []

        critique: Critique | None = None

        iteration = 0

        # -----------------------------------------------------
        # Research iterations
        # -----------------------------------------------------

        for iteration in range(
            1,
            self.max_iterations + 1,
        ):

            print(
                "\n"
                + "=" * 62
            )

            print(
                f"RESEARCH ITERATION {iteration}"
            )

            print(
                "=" * 62
            )

            state.iteration = iteration

            self.event_logger.emit(
                event="iteration_started",
                iteration=iteration,
            )

            # -------------------------------------------------
            # Search
            # -------------------------------------------------

            sources = self.researcher.search(
                plan
            )

            existing_source_ids = {
                source.id
                for source in all_sources
            }

            new_sources = [
                source
                for source in sources
                if source.id
                not in existing_source_ids
            ]

            all_sources.extend(
                new_sources
            )

            print(
                f"New sources: "
                f"{len(new_sources)}"
            )

            # -------------------------------------------------
            # Rank sources
            # -------------------------------------------------

            ranked_sources = (
                self.source_ranker.rank(
                    all_sources,
                    plan.question,
                )
            )

            selected_sources = (
                self.source_ranker.select(
                    ranked_sources
                )
            )

            # -------------------------------------------------
            # Evidence extraction
            # -------------------------------------------------

            analyzed_source_ids = {
                str(analysis.source_id)
                for analysis in all_analyses
            }

            for source in selected_sources:

                if str(source.id) in analyzed_source_ids:
                    continue

                analysis = self.evidence_agent.analyze(
                    source
                )

                if analysis is None:
                    continue

                all_analyses.append(
                    analysis
                )

                analyzed_source_ids.add(
                    str(source.id)
                )

                print(
                    f"Analyzed: "
                    f"{source.title}"
                )

            # -------------------------------------------------
            # Collect claims
            # -------------------------------------------------

            claims = [
                claim
                for analysis in all_analyses
                for claim in analysis.claims
            ]

            # -------------------------------------------------
            # Claim relationship analysis
            # -------------------------------------------------

            relationships = (
                self.claim_analyzer.analyze(
                    claims
                )
            )

            all_relationships = (
                relationships
            )

            # -------------------------------------------------
            # Critic
            # -------------------------------------------------

            critique = self.critic.critique(
                plan=plan,
                sources=all_sources,
                analyses=all_analyses,
                relationships=all_relationships,
            )

            # -------------------------------------------------
            # Update research state
            # -------------------------------------------------

            state.sources_found = len(
                all_sources
            )

            state.claims_found = len(
                claims
            )

            state.relationships_found = len(
                all_relationships
            )

            state.confidence = (
                critique.overall_confidence
            )

            # -------------------------------------------------
            # Iteration event
            # -------------------------------------------------

            self.event_logger.emit(
                event="iteration_completed",
                iteration=iteration,
                data={
                    "sources": len(all_sources),
                    "claims": len(claims),
                    "relationships": len(
                        all_relationships
                    ),
                    "confidence": (
                        critique.overall_confidence
                    ),
                    "sufficient": (
                        critique.sufficient
                    ),
                },
            )

            # -------------------------------------------------
            # Console output
            # -------------------------------------------------

            print(
                f"\nSufficient: "
                f"{critique.sufficient}"
            )

            print(
                f"Confidence: "
                f"{critique.overall_confidence:.2f}"
            )

            # -------------------------------------------------
            # Research complete
            # -------------------------------------------------

            if critique.sufficient:

                state.status = "completed"

                state.completed_at = (
                    datetime.now(
                        timezone.utc
                    )
                )

                self.event_logger.emit(
                    event="research_completed",
                    iteration=iteration,
                    data={
                        "confidence": (
                            critique.overall_confidence
                        ),
                    },
                )

                print(
                    "\nResearch is sufficient."
                )

                break

            # -------------------------------------------------
            # Continue research
            # -------------------------------------------------

            print(
                "\nResearch is insufficient."
            )

            if iteration < self.max_iterations:

                print(
                    "Continuing research..."
                )

        # -----------------------------------------------------
        # Maximum iterations reached
        # -----------------------------------------------------

        if (
            critique is not None
            and not critique.sufficient
            and iteration >= self.max_iterations
        ):

            state.status = "max_iterations"

            state.completed_at = (
                datetime.now(
                    timezone.utc
                )
            )

            self.event_logger.emit(
                event="research_max_iterations",
                iteration=iteration,
                data={
                    "confidence": (
                        critique.overall_confidence
                    ),
                },
            )

            print(
                "\nMaximum research iterations reached."
            )

        # -----------------------------------------------------
        # Safety check
        # -----------------------------------------------------

        if critique is None:

            state.status = "failed"

            state.completed_at = (
                datetime.now(
                    timezone.utc
                )
            )

            raise RuntimeError(
                "Research loop completed without "
                "producing a critique."
            )

        # -----------------------------------------------------
        # Return result
        # -----------------------------------------------------

        return ResearchResult(
            plan=plan,
            sources=all_sources,
            analyses=all_analyses,
            relationships=all_relationships,
            critique=critique,
            iterations=iteration,
            state=state,
            events=self.event_logger.all(),
        )