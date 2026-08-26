import json
from pathlib import Path
from uuid import UUID

from app.core.research_loop import ResearchResult


class ResearchRunStore:

    def __init__(
        self,
        directory: str = "data/runs",
    ):
        self.directory = Path(directory)

        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        result: ResearchResult,
    ) -> Path:

        run_id = result.state.run_id

        path = (
            self.directory
            / f"{run_id}.json"
        )

        payload = result_to_dict(
            result
        )

        path.write_text(
            json.dumps(
                payload,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        return path

    def load(
        self,
        run_id: UUID,
    ) -> dict:

        path = (
            self.directory
            / f"{run_id}.json"
        )

        if not path.exists():

            raise FileNotFoundError(
                f"Research run not found: {run_id}"
            )

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    def exists(
        self,
        run_id: UUID,
    ) -> bool:

        path = (
            self.directory
            / f"{run_id}.json"
        )

        return path.exists()

    def list_runs(self) -> list[UUID]:

        run_ids = []

        for path in self.directory.glob(
            "*.json"
        ):

            try:

                run_ids.append(
                    UUID(path.stem)
                )

            except ValueError:
                continue

        return sorted(
            run_ids,
            key=lambda run_id: run_id.hex,
            reverse=True,
        )


def result_to_dict(
    result: ResearchResult,
) -> dict:

    return {
        "plan": result.plan.model_dump(
            mode="json"
        ),

        "sources": [
            source.model_dump(
                mode="json"
            )
            for source in result.sources
        ],

        "analyses": [
            analysis.model_dump(
                mode="json"
            )
            for analysis in result.analyses
        ],

        "relationships": [
            relationship.model_dump(
                mode="json"
            )
            for relationship
            in result.relationships
        ],

        "critique": result.critique.model_dump(
            mode="json"
        ),

        "iterations": result.iterations,

        "state": result.state.model_dump(
            mode="json"
        ),

        "events": [
            event.model_dump(
                mode="json"
            )
            for event in result.events
        ],
    }