import json
from pathlib import Path

from app.models.schemas import ResearchRun


class RunStore:

    def __init__(self, base_dir: str = "research"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, run: ResearchRun) -> Path:
        run_dir = self.base_dir / run.id
        run_dir.mkdir(parents=True, exist_ok=True)

        run_file = run_dir / "run.json"

        run_file.write_text(
            json.dumps(
                run.model_dump(mode="json"),
                indent=2,
            ),
            encoding="utf-8",
        )

        return run_file