from app.core.retry import retry


def test_retry_succeeds_after_failure():

    attempts = 0

    def unstable_function():

        nonlocal attempts

        attempts += 1

        if attempts < 3:
            raise RuntimeError("Temporary failure")

        return "success"

    result = retry(
        unstable_function,
        max_attempts=3,
        delay=0,
    )

    assert result == "success"
    assert attempts == 3