from dataclasses import dataclass
from threading import Thread
from uuid import UUID


@dataclass
class ResearchJob:
    run_id: UUID
    status: str = "queued"
    error: str | None = None


class ResearchJobManager:

    def __init__(self):
        self.jobs: dict[str, ResearchJob] = {}

    def create(
        self,
        run_id: UUID,
    ) -> ResearchJob:

        job = ResearchJob(
            run_id=run_id,
        )

        self.jobs[str(run_id)] = job

        return job

    def get(
        self,
        run_id: UUID,
    ) -> ResearchJob | None:

        return self.jobs.get(
            str(run_id)
        )

    def set_status(
        self,
        run_id: UUID,
        status: str,
        error: str | None = None,
    ):

        job = self.get(run_id)

        if job is None:
            return

        job.status = status
        job.error = error