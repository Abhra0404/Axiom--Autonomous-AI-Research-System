import sys
from datetime import datetime, timezone
from uuid import uuid4

from app.agents.critic import CriticAgent
from app.agents.evidence import EvidenceAgent
from app.agents.planner import Planner
from app.agents.researcher import Researcher
from app.core.gemini_llm import GeminiProvider
from app.core.research_loop import ResearchLoop
from app.core.run_store import RunStore
from app.core.source_ingestor import SourceIngestor
from app.core.source_manager import SourceManager
from app.core.source_ranker import SourceRanker
from app.core.tavily_search import TavilySearchProvider
from app.models.schemas import ResearchRequest, ResearchRun
from app.agents.report import ReportAgent
from app.core.report_renderer import ReportRenderer
from app.core.report_store import ReportStore
from app.core.source_cache import SourceCache
from app.core.evidence_cache import EvidenceCache



def run_research(topic: str) -> None:

    # =========================================================
    # 1. Research Request
    # =========================================================

    request = ResearchRequest(
        topic=topic,
        depth="deep",
    )

    print("\n" + "=" * 70)
    print("AXIOM — AUTONOMOUS RESEARCH SYSTEM")
    print("=" * 70)

    print(f"\nResearch question:")
    print(f"  {request.topic}")

    # =========================================================
    # 2. Planner
    # =========================================================

    print("\n[1/3] Creating research plan...")

    planner = Planner()

    plan = planner.create_plan(request)

    print(f"\nObjectives: {len(plan.objectives)}")

    for objective in plan.objectives:
        print(f"  - {objective}")

    print(f"\nSub-questions: {len(plan.sub_questions)}")

    for question in plan.sub_questions:
        print(f"  - {question}")

    print(f"\nInitial search queries:")

    for query in plan.search_queries:
        print(f"  - {query}")

    # =========================================================
    # 3. Build Agents + Services
    # =========================================================

    print("\n[2/3] Starting autonomous research loop...")

    search_provider = TavilySearchProvider()

    source_cache = SourceCache()

    source_ingestor = SourceIngestor(
        cache=source_cache
    )

    source_manager = SourceManager()

    researcher = Researcher(
        search_provider,
        source_ingestor,
        source_manager,
    )

    source_ranker = SourceRanker()

    llm = GeminiProvider()

    evidence_cache = EvidenceCache()

    evidence_agent = EvidenceAgent(
        llm,
        cache=evidence_cache,
    )

    critic = CriticAgent(
        llm
    )

    research_loop = ResearchLoop(
        planner=planner,
        researcher=researcher,
        evidence_agent=evidence_agent,
        critic=critic,
        source_ranker=source_ranker,
        max_iterations=3,
    )

    # =========================================================
    # 4. Execute Autonomous Research
    # =========================================================

    result = research_loop.run(
        plan
    )
    print("\nGenerating final research report...")

    report_agent = ReportAgent(llm)

    report = report_agent.generate(
        result.plan,
        result.sources,
        result.analyses,
        result.critique,
    )

    renderer = ReportRenderer()

    all_claims = [
    claim
    for analysis in result.analyses
    for claim in analysis.claims
    ]

    all_evidence = [
        item
        for analysis in result.analyses
        for item in analysis.evidence
    ]

    markdown_report = renderer.render(
        report,
        sources=result.sources,
        claims=all_claims,
        evidence=all_evidence,
    )

    # =========================================================
    # 5. Display Final Results
    # =========================================================

    print("\n" + "=" * 70)
    print("FINAL RESEARCH RESULTS")
    print("=" * 70)

    print(
        f"\nIterations completed:"
        f" {result.iterations}"
    )

    print(
        f"\nSources collected:"
        f" {len(result.sources)}"
    )

    print(
        f"\nEvidence analyses:"
        f" {len(result.analyses)}"
    )

    # ---------------------------------------------------------
    # Claims
    # ---------------------------------------------------------

    total_claims = 0
    total_evidence = 0

    print("\n" + "-" * 70)
    print("CLAIMS")
    print("-" * 70)

    for analysis in result.analyses:

        total_claims += len(
            analysis.claims
        )

        total_evidence += len(
            analysis.evidence
        )

        for claim in analysis.claims:

            print(
                f"\n• {claim.statement}"
            )

            print(
                f"  Confidence: "
                f"{claim.confidence:.2f}"
            )

    # ---------------------------------------------------------
    # Critique
    # ---------------------------------------------------------

    print("\n" + "-" * 70)
    print("CRITIQUE")
    print("-" * 70)

    critique = result.critique

    print(
        f"\nSufficient:"
        f" {critique.sufficient}"
    )

    print(
        f"Overall confidence:"
        f" {critique.overall_confidence:.2f}"
    )

    if critique.strengths:

        print("\nStrengths:")

        for strength in critique.strengths:
            print(f"  - {strength}")

    if critique.weaknesses:

        print("\nWeaknesses:")

        for weakness in critique.weaknesses:
            print(f"  - {weakness}")

    if critique.missing_information:

        print("\nMissing information:")

        for item in critique.missing_information:
            print(f"  - {item}")

    if critique.follow_up_questions:

        print("\nFollow-up questions:")

        for question in critique.follow_up_questions:
            print(f"  - {question}")

    # =========================================================
    # 6. Persist Research Run
    # =========================================================

    print("\n[3/3] Saving research run...")

    research_run = ResearchRun(
        id=f"run_{uuid4().hex[:12]}",
        question=request.topic,
        created_at=datetime.now(
            timezone.utc
        ),
        plan=result.plan,
        sources=result.sources,
        analyses=result.analyses,
    )

    store = RunStore()

    run_file = store.save(
        research_run
    )

    # =========================================================
    # 7. Save Research Report
    # =========================================================

    report_store = ReportStore()

    report_file = report_store.save(
        research_run.id,
        markdown_report,
    )

    print(
        f"\nReport saved to:"
        f"\n  {report_file}"
    )

    # =========================================================
    # 8. Summary
    # =========================================================

    print("\n" + "=" * 70)
    print("AXIOM RUN COMPLETE")
    print("=" * 70)

    print(
        f"\nRun ID:"
        f"\n  {research_run.id}"
    )

    print(
        f"\nIterations:"
        f"\n  {result.iterations}"
    )

    print(
        f"\nSources:"
        f"\n  {len(result.sources)}"
    )

    print(
        f"\nClaims:"
        f"\n  {total_claims}"
    )

    print(
        f"\nEvidence items:"
        f"\n  {total_evidence}"
    )

    print(
        f"\nResearch sufficient:"
        f"\n  {critique.sufficient}"
    )

    print(
        f"\nConfidence:"
        f"\n  {critique.overall_confidence:.2f}"
    )

    print(
        f"\nSaved to:"
        f"\n  {run_file}"
    )

    print("\n" + "=" * 70)


if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            'Usage: python -m app.run '
            '"your research question"'
        )

        sys.exit(1)

    topic = " ".join(
        sys.argv[1:]
    )

    run_research(topic)