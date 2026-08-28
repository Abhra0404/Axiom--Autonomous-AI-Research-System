from threading import Lock


class LLMRequestBudget:

    def __init__(
        self,
        max_requests: int = 20,
    ):
        if max_requests < 1:
            raise ValueError(
                "max_requests must be at least 1"
            )

        self.max_requests = max_requests
        self._requests = 0
        self._lock = Lock()

    @property
    def requests_used(self) -> int:
        with self._lock:
            return self._requests

    @property
    def requests_remaining(self) -> int:
        with self._lock:
            return max(
                0,
                self.max_requests - self._requests,
            )

    def acquire(self) -> bool:

        with self._lock:

            if self._requests >= self.max_requests:
                return False

            self._requests += 1

            return True

    def reset(self) -> None:

        with self._lock:
            self._requests = 0