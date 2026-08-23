import sys
from datetime import datetime, timezone
from uuid import uuid4

from app.agents.evidence import EvidenceAgent
from app.agents.planner import Planner
from app.agents.researcher import Researcher
from app.core.gemini_llm import GeminiProvider
from app.core.run_store import RunStore
from app.core.source_ingestor import SourceIngestor
from app.core.source_manager import SourceManager
from app.core.tavily_search import TavilySearchProvider
from app.models.schemas import ResearchRequest, ResearchRun
from app.core.source_ranker import SourceRanker

def run_research(topic: str) -> None:
    # ---------------------------------------------------------
    # 1. Create research request
    # ---------------------------------------------------------

    request = ResearchRequest(
        topic=topic,
        depth="deep",
    )

    print("\n" + "=" * 70)
    print("AXIOM — AUTONOMOUS RESEARCH SYSTEM")
    print("=" * 70)

    print("\n[1/5] Creating research plan...")

    # ---------------------------------------------------------
    # 2. Create research plan
    # ---------------------------------------------------------

    planner = Planner()
    plan = planner.create_plan(request)

    print(f"\nResearch question:")
    print(f"  {plan.question}")

    print(f"\nObjectives: {len(plan.objectives)}")
    for objective in plan.objectives:
        print(f"  - {objective}")

    print(f"\nSub-questions: {len(plan.sub_questions)}")
    for question in plan.sub_questions:
        print(f"  - {question}")

    print(f"\nSearch queries: {len(plan.search_queries)}")
    for query in plan.search_queries:
        print(f"  - {query}")

    # ---------------------------------------------------------
    # 3. Research
    # ---------------------------------------------------------

    print("\n[2/5] Searching for sources...")

    researcher = Researcher(
        TavilySearchProvider(),
        SourceIngestor(),
        SourceManager(),
    )

    sources = researcher.search(plan)

    ranker = SourceRanker()

    sources = ranker.rank(
        sources,
        request.topic,
    )

    sources = ranker.select(
        sources,
        top_k=3,
    )
    print("\nRanked sources:")

    for source in sources:
        print(
            f"  {source.relevance_score:.2f} "
            f"| {source.title}"
        )

    if not sources:
        print("\nNo usable sources found.")
        print("Research run terminated.")
        return

    # ---------------------------------------------------------
    # 4. Evidence extraction
    # ---------------------------------------------------------

    print("\n[3/5] Extracting evidence...")

    llm = GeminiProvider()
    evidence_agent = EvidenceAgent(llm)

    analyses = []

    for index, source in enumerate(sources, start=1):

        print(
            f"\nAnalyzing source "
            f"{index}/{len(sources)}: {source.title}"
        )

        try:
            analysis = evidence_agent.analyze(source)

            analyses.append(
                {
                    "source": source,
                    "analysis": analysis,
                }
            )

            print(
                f"  Claims extracted: "
                f"{len(analysis.claims)}"
            )

            print(
                f"  Evidence extracted: "
                f"{len(analysis.evidence)}"
            )

        except Exception as error:
            print(f"  Failed to analyze source: {error}")

    # ---------------------------------------------------------
    # 5. Display findings
    # ---------------------------------------------------------

    print("\n[4/5] Research findings")

    print("\n" + "=" * 70)

    total_claims = 0
    total_evidence = 0

    for item in analyses:

        source = item["source"]
        analysis = item["analysis"]

        total_claims += len(analysis.claims)
        total_evidence += len(analysis.evidence)

        print("\n" + "=" * 70)
        print(source.title)
        print(str(source.url))
        print("=" * 70)

        if not analysis.claims:
            print("\nNo claims extracted.")
            continue

        for claim in analysis.claims:

            print(f"\nClaim:")
            print(f"  {claim.statement}")

            print(
                f"Confidence: "
                f"{claim.confidence:.2f}"
            )

            related_evidence = [
                evidence
                for evidence in analysis.evidence
                if evidence.claim_id == claim.id
            ]

            for evidence in related_evidence:

                print("\nEvidence:")
                print(f"  {evidence.content}")

                print(
                    f"Strength: "
                    f"{evidence.strength}"
                )

    # ---------------------------------------------------------
    # 6. Create research run
    # ---------------------------------------------------------

    research_run = ResearchRun(
        id=f"run_{uuid4().hex[:12]}",
        question=request.topic,
        created_at=datetime.now(timezone.utc),
        plan=plan,
        sources=sources,
        analyses=[
            item["analysis"]
            for item in analyses
        ],
    )

    # ---------------------------------------------------------
    # 7. Persist research run
    # ---------------------------------------------------------

    store = RunStore()

    run_file = store.save(research_run)

    # ---------------------------------------------------------
    # 8. Final summary
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("[5/5] RESEARCH RUN COMPLETE")
    print("=" * 70)

    print(f"\nResearch Run ID:")
    print(f"  {research_run.id}")

    print(f"\nSources:")
    print(f"  {len(sources)}")

    print(f"\nClaims:")
    print(f"  {total_claims}")

    print(f"\nEvidence:")
    print(f"  {total_evidence}")

    print(f"\nSaved to:")
    print(f"  {run_file}")

    print("\n" + "=" * 70)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(
            'Usage: python -m app.run '
            '"your research question"'
        )
        sys.exit(1)

    topic = " ".join(sys.argv[1:])

    run_research(topic)