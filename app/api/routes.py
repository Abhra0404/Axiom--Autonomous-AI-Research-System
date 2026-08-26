from threading import Thread
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.api.jobs import ResearchJobManager
from app.api.schemas import (
    ResearchRequestAPI,
    ResearchResponse,
)
from app.core.research_run_store import ResearchRunStore


router = APIRouter()

run_store = ResearchRunStore()
job_manager = ResearchJobManager()


def execute_research(
    topic: str,
    run_id: UUID,
):
    from app.run import run_research

    job_manager.set_status(
        run_id,
        "running",
    )

    try:

        result = run_research(
            topic
        )

        # The research loop creates its own
        # run ID, so this job ID must correspond
        # to the persisted result.
        job_manager.set_status(
            result.state.run_id,
            "completed",
        )

    except Exception as exc:

        job_manager.set_status(
            run_id,
            "failed",
            error=str(exc),
        )


@router.get("/health")
def health():

    return {
        "status": "ok",
        "service": "axiom",
    }


@router.post(
    "/research",
    status_code=202,
)
def create_research(
    request: ResearchRequestAPI,
):

    run_id = uuid4()

    job_manager.create(
        run_id
    )

    thread = Thread(
        target=execute_research,
        args=(
            request.topic,
            run_id,
        ),
        daemon=True,
    )

    thread.start()

    return JSONResponse(
        status_code=202,
        content={
            "run_id": str(run_id),
            "status": "queued",
        },
    )


@router.get("/research")
def list_research_runs():

    runs = run_store.list_runs()

    return {
        "runs": [
            str(run_id)
            for run_id in runs
        ]
    }


@router.get("/research/{run_id}")
def get_research_run(
    run_id: UUID,
):

    try:

        result = run_store.load(
            run_id
        )

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail="Research run not found",
        )

    return result


@router.get(
    "/research/{run_id}/status"
)
def get_research_status(
    run_id: UUID,
):

    job = job_manager.get(
        run_id
    )

    if job is not None:

        response = {
            "run_id": str(
                run_id
            ),
            "status": job.status,
        }

        if job.error:
            response["error"] = job.error

        return response

    if run_store.exists(
        run_id
    ):

        return {
            "run_id": str(
                run_id
            ),
            "status": "completed",
        }

    raise HTTPException(
        status_code=404,
        detail="Research run not found",
    )