from app.agents.evidence import EvidenceAgent
from app.core.ollama_llm import OllamaProvider
from app.models.schemas import Source


source = Source(
    id="test-001",
    title="Retrieval-Augmented Generation",
    url="https://example.com",
    source_type="article",
    content="""
    Retrieval-Augmented Generation combines information
    retrieval with text generation. RAG can provide language
    models with external information that was not contained
    in their original training data. This can improve the
    factual grounding of generated responses.
    """,
)

llm = OllamaProvider()

agent = EvidenceAgent(llm)

result = agent.analyze(source)

print("\n=== CLAIMS ===")

for claim in result.claims:
    print(f"\nClaim: {claim.statement}")
    print(f"Confidence: {claim.confidence}")

print("\n=== EVIDENCE ===")

for evidence in result.evidence:
    print(f"\nEvidence: {evidence.content}")
    print(f"Strength: {evidence.strength}")