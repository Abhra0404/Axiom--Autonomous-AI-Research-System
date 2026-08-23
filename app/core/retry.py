import time
from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T")


def retry(
    func: Callable[[], T],
    max_attempts: int = 3,
    delay: float = 2.0,
) -> T:

    last_error = None

    for attempt in range(max_attempts):

        try:
            return func()

        except Exception as error:
            last_error = error

            if attempt == max_attempts - 1:
                raise

            wait_time = delay * (2 ** attempt)

            print(
                f"Retrying after "
                f"{wait_time:.1f}s..."
            )

            time.sleep(wait_time)

    raise last_error