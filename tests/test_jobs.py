from uuid import uuid4

from app.api.jobs import ResearchJobManager


def test_job_manager_create():

    manager = ResearchJobManager()

    run_id = uuid4()

    job = manager.create(
        run_id
    )

    assert job.run_id == run_id
    assert job.status == "queued"


def test_job_manager_get():

    manager = ResearchJobManager()

    run_id = uuid4()

    manager.create(
        run_id
    )

    job = manager.get(
        run_id
    )

    assert job is not None
    assert job.run_id == run_id


def test_job_manager_update():

    manager = ResearchJobManager()

    run_id = uuid4()

    manager.create(
        run_id
    )

    manager.set_status(
        run_id,
        "running",
    )

    job = manager.get(
        run_id
    )

    assert job.status == "running"


def test_job_manager_missing_job():

    manager = ResearchJobManager()

    job = manager.get(
        uuid4()
    )

    assert job is None