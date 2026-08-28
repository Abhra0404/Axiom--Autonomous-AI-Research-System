from app.core.llm_budget import (
    LLMRequestBudget,
)


def test_budget_allows_requests():

    budget = LLMRequestBudget(
        max_requests=2
    )

    assert budget.acquire() is True
    assert budget.acquire() is True

    assert budget.requests_used == 2
    assert budget.requests_remaining == 0


def test_budget_blocks_excess_requests():

    budget = LLMRequestBudget(
        max_requests=1
    )

    assert budget.acquire() is True
    assert budget.acquire() is False


def test_budget_reset():

    budget = LLMRequestBudget(
        max_requests=1
    )

    assert budget.acquire() is True
    assert budget.acquire() is False

    budget.reset()

    assert budget.acquire() is True