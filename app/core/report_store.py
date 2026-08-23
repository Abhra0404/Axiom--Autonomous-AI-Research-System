from pathlib import Path

from app.models.schemas import ResearchReport


class ReportStore:

    def __init__(
        self,
        base_dir: str = "reports",
    ):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        run_id: str,
        report: str,
    ) -> Path:

        report_file = (
            self.base_dir
            / f"{run_id}.md"
        )

        report_file.write_text(
            report,
            encoding="utf-8",
        )

        return report_file