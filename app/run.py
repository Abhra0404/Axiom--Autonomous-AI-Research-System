import sys

from app.agents.evidence import EvidenceAgent
from app.agents.planner import Planner
from app.agents.researcher import Researcher
from app.core.ollama_llm import OllamaProvider
from app.core.source_ingestor import SourceIngestor
from app.core.source_manager import SourceManager
from app.core.tavily_search import TavilySearchProvider
from app.models.schemas import ResearchRequest


def run_research(topic: str):

    # 1. Create research request
    request = ResearchRequest(
        topic=topic,
        depth="deep",
    )

    print("\n[1/5] Creating research plan...")

    # 2. Create research plan
    planner = Planner()
    plan = planner.create_plan(request)

    print(f"Research question: {plan.question}")
    print(f"Sub-questions: {len(plan.sub_questions)}")
    print(f"Search queries: {len(plan.search_queries)}")

    # 3. Research
    print("\n[2/5] Searching for sources...")

    researcher = Researcher(
        TavilySearchProvider(),
        SourceIngestor(),
        SourceManager(),
    )

    sources = researcher.search(plan)

    print(f"Sources found: {len(sources)}")

    if not sources:
        print("No usable sources found.")
        return

    # 4. Evidence extraction
    print("\n[3/5] Extracting evidence...")

    llm = OllamaProvider()
    evidence_agent = EvidenceAgent(llm)

    analyses = []

    for index, source in enumerate(sources, start=1):

        print(
            f"Analyzing source {index}/{len(sources)}: "
            f"{source.title}"
        )

        analysis = evidence_agent.analyze(source)

        analyses.append(
            {
                "source": source,
                "analysis": analysis,
            }
        )

    # 5. Display results
    print("\n[4/5] Research findings\n")

    for item in analyses:

        source = item["source"]
        analysis = item["analysis"]

        print("=" * 70)
        print(source.title)
        print("=" * 70)

        for claim in analysis.claims:

            print(f"\nClaim: {claim.statement}")
            print(f"Confidence: {claim.confidence:.2f}")

            related_evidence = [
                evidence
                for evidence in analysis.evidence
                if evidence.claim_id == claim.id
            ]

            for evidence in related_evidence:
                print(f"Evidence: {evidence.content}")
                print(f"Strength: {evidence.strength}")

    print("\n[5/5] Research run complete.")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(
            'Usage: python -m app.run "your research question"'
        )
        sys.exit(1)

    topic = " ".join(sys.argv[1:])

    run_research(topic)