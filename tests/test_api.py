from uuid import uuid4
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok",
        "service": "axiom",
    }


def test_list_research_runs():

    response = client.get(
        "/research"
    )

    assert response.status_code == 200

    assert "runs" in response.json()


@patch("app.api.routes.Thread")
def test_create_research(
    mock_thread,
):

    response = client.post(
        "/research",
        json={
            "topic": "Does RAG reduce hallucinations?"
        },
    )

    assert response.status_code == 202

    data = response.json()

    assert "run_id" in data

    assert data["status"] == "queued"

    mock_thread.assert_called_once()

    mock_thread.return_value.start.assert_called_once()


def test_invalid_research_request():

    response = client.post(
        "/research",
        json={
            "topic": "hi"
        },
    )

    assert response.status_code == 422


def test_research_status_not_found():

    run_id = uuid4()

    response = client.get(
        f"/research/{run_id}/status"
    )

    assert response.status_code == 404


def test_research_run_not_found():

    run_id = uuid4()

    response = client.get(
        f"/research/{run_id}"
    )

    assert response.status_code == 404