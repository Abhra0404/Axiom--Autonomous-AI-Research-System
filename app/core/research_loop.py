from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.core.event_logger import ResearchEventLogger
from app.models.events import ResearchEvent
from app.models.schemas import (
    ClaimRelationship,
    Critique,
    EvidenceAnalysis,
    ResearchPlan,
    Source,
)
from app.models.state import ResearchState


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
        run_id: UUID | None = None,
    ) -> ResearchResult:

        # =====================================================
        # Initialize state
        # =====================================================

        state = ResearchState(
            run_id=run_id or uuid4(),
            status="running",
            started_at=datetime.now(
                timezone.utc
            ),
        )

        self.event_logger.emit(
            event="research_started",
            iteration=0,
        )

        # =====================================================
        # Research collections
        # =====================================================

        all_sources: list[Source] = []

        all_analyses: list[
            EvidenceAnalysis
        ] = []

        all_relationships: list[
            ClaimRelationship
        ] = []

        critique: Critique | None = None

        iteration = 0

        current_plan = plan

        # =====================================================
        # Research iterations
        # =====================================================

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

            # =================================================
            # Search
            # =================================================

            sources = self.researcher.search(
                current_plan
            )

            if sources is None:
                sources = []

            # -------------------------------------------------
            # Remove sources already discovered
            # -------------------------------------------------

            existing_source_ids = {
                str(source.id)
                for source in all_sources
                if source is not None
            }

            new_sources = []

            for source in sources:

                if source is None:
                    continue

                source_id = str(
                    source.id
                )

                if source_id in existing_source_ids:
                    continue

                existing_source_ids.add(
                    source_id
                )

                new_sources.append(
                    source
                )

            all_sources.extend(
                new_sources
            )

            print(
                f"New sources: "
                f"{len(new_sources)}"
            )

            # =================================================
            # Rank sources
            # =================================================

            if all_sources:

                ranked_sources = self.source_ranker.rank(
                    all_sources,
                    current_plan.question,
                )

                all_sources = ranked_sources

                selected_sources = (
                    self.source_ranker.select(
                        ranked_sources
                    )
                )

            else:

                selected_sources = []

            # =================================================
            # Evidence extraction
            # =================================================

            analyzed_source_ids = {
                str(analysis.source_id)
                for analysis in all_analyses
            }

            newly_analyzed = 0

            for source in selected_sources:

                if source is None:
                    continue

                source_id = str(
                    source.id
                )

                # ---------------------------------------------
                # Skip already analyzed sources
                # ---------------------------------------------

                if source_id in analyzed_source_ids:
                    continue

                try:

                    analysis = (
                        self.evidence_agent.analyze(
                            source
                        )
                    )

                except Exception as exc:

                    print(
                        f"Evidence analysis failed "
                        f"for {source.title}: {exc}"
                    )

                    self.event_logger.emit(
                        event="evidence_analysis_failed",
                        iteration=iteration,
                        data={
                            "source_id": source_id,
                            "error": str(exc),
                        },
                    )

                    continue

                if analysis is None:
                    continue

                all_analyses.append(
                    analysis
                )

                analyzed_source_ids.add(
                    source_id
                )

                newly_analyzed += 1

                print(
                    f"Analyzed: "
                    f"{source.title}"
                )

            # =================================================
            # Collect claims
            # =================================================

            claims = [
                claim
                for analysis in all_analyses
                for claim in analysis.claims
            ]

            # =================================================
            # Claim relationship analysis
            # =================================================

            relationships = (
                self.claim_analyzer.analyze(
                    claims
                )
            )

            # -------------------------------------------------
            # Merge relationships instead of replacing them
            # -------------------------------------------------

            existing_relationships = {
                (
                    relationship.claim_a,
                    relationship.claim_b,
                    relationship.relationship,
                )
                for relationship
                in all_relationships
            }

            for relationship in relationships:

                relationship_key = (
                    relationship.claim_a,
                    relationship.claim_b,
                    relationship.relationship,
                )

                if (
                    relationship_key
                    not in existing_relationships
                ):

                    all_relationships.append(
                        relationship
                    )

                    existing_relationships.add(
                        relationship_key
                    )

            # =================================================
            # Critic
            # =================================================

            critique = self.critic.critique(
                plan=current_plan,
                sources=all_sources,
                analyses=all_analyses,
                relationships=all_relationships,
            )

            # =================================================
            # Update research state
            # =================================================

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
                float(
                    critique.overall_confidence
                )
            )

            # =================================================
            # Iteration event
            # =================================================

            self.event_logger.emit(
                event="iteration_completed",
                iteration=iteration,
                data={
                    "sources": len(
                        all_sources
                    ),
                    "new_sources": len(
                        new_sources
                    ),
                    "newly_analyzed": (
                        newly_analyzed
                    ),
                    "claims": len(
                        claims
                    ),
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

            # =================================================
            # Console output
            # =================================================

            print(
                f"\nSufficient: "
                f"{critique.sufficient}"
            )

            print(
                f"Confidence: "
                f"{critique.overall_confidence:.2f}"
            )

            # =================================================
            # Research complete
            # =================================================

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
                        "sources": len(
                            all_sources
                        ),
                        "claims": len(
                            claims
                        ),
                    },
                )

                print(
                    "\nResearch is sufficient."
                )

                break

            # =================================================
            # Continue research
            # =================================================

            print(
                "\nResearch is insufficient."
            )

            if iteration >= self.max_iterations:
                continue

            # =================================================
            # Generate follow-up research plan
            # =================================================

            follow_up_questions = (
                critique.follow_up_questions
            )

            if follow_up_questions:

                follow_up_queries = [
                    question
                    for question
                    in follow_up_questions
                    if isinstance(
                        question,
                        str,
                    )
                    and question.strip()
                ]

                if follow_up_queries:

                    current_plan = self._build_follow_up_plan(
                        current_plan,
                        follow_up_queries,
                    )

                    print(
                        "\nFollow-up research:"
                    )

                    for query in (
                        current_plan.search_queries
                    ):
                        print(
                            f"  - {query}"
                        )

                    self.event_logger.emit(
                        event="follow_up_research_planned",
                        iteration=iteration,
                        data={
                            "questions": (
                                follow_up_queries
                            ),
                            "search_queries": (
                                current_plan.search_queries
                            ),
                        },
                    )

                else:

                    print(
                        "\nNo valid follow-up "
                        "questions generated."
                    )

            else:

                print(
                    "\nNo follow-up questions "
                    "generated."
                )

        # =====================================================
        # Maximum iterations reached
        # =====================================================

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
                    "sources": len(
                        all_sources
                    ),
                    "claims": len(
                        [
                            claim
                            for analysis
                            in all_analyses
                            for claim
                            in analysis.claims
                        ]
                    ),
                },
            )

            print(
                "\nMaximum research iterations reached."
            )

        # =====================================================
        # Safety check
        # =====================================================

        if critique is None:

            state.status = "failed"

            state.completed_at = (
                datetime.now(
                    timezone.utc
                )
            )

            self.event_logger.emit(
                event="research_failed",
                iteration=iteration,
            )

            raise RuntimeError(
                "Research loop completed without "
                "producing a critique."
            )

        # =====================================================
        # Return result
        # =====================================================

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

    # =========================================================
    # Follow-up plan
    # =========================================================

    def _build_follow_up_plan(
        self,
        previous_plan: ResearchPlan,
        questions: list[str],
    ) -> ResearchPlan:

        existing_queries = {
            query.strip().lower()
            for query
            in previous_plan.search_queries
            if isinstance(query, str)
        }

        new_queries = []

        for question in questions:

            normalized = (
                question.strip()
            )

            if not normalized:
                continue

            if (
                normalized.lower()
                in existing_queries
            ):
                continue

            new_queries.append(
                normalized
            )

        return ResearchPlan(
            question=previous_plan.question,
            objectives=previous_plan.objectives,
            sub_questions=questions,
            search_queries=new_queries,
        )