from app.models.schemas import (
    Claim,
    Evidence,
    Source,
)


class ProvenanceResolver:

    def __init__(
        self,
        sources: list[Source],
        claims: list[Claim],
        evidence: list[Evidence],
    ):
        self.sources = {
            source.id: source
            for source in sources
        }

        self.claims = {
            claim.id: claim
            for claim in claims
        }

        self.evidence = {
            item.id: item
            for item in evidence
        }

    def get_claim_evidence(
        self,
        claim: Claim,
    ) -> list[Evidence]:

        return [
            self.evidence[evidence_id]
            for evidence_id in claim.evidence_ids
            if evidence_id in self.evidence
        ]

    def get_claim_source(
        self,
        claim: Claim,
    ) -> Source | None:

        return self.sources.get(
            claim.source_id
        )