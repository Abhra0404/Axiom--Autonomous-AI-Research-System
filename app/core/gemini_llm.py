import os

from google import genai
from google.genai import types

from app.core.llm import LLMProvider
from app.core.llm_budget import LLMRequestBudget
from app.core.retry import retry


class GeminiQuotaExceededError(
    RuntimeError
):
    pass


class GeminiProvider(LLMProvider):

    def __init__(
        self,
        model: str | None = None,
        budget: LLMRequestBudget | None = None,
    ):

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model or os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash",
        )

        self.budget = (
            budget
            or LLMRequestBudget(
                max_requests=int(
                    os.getenv(
                        "GEMINI_MAX_REQUESTS",
                        "20",
                    )
                )
            )
        )

    def _acquire_request(self) -> None:

        if not self.budget.acquire():

            raise GeminiQuotaExceededError(
                "LLM request budget exhausted. "
                f"Limit: {self.budget.max_requests}, "
                f"used: {self.budget.requests_used}."
            )

    def generate(
        self,
        prompt: str,
    ) -> str:

        self._acquire_request()

        try:

            response = (
                self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
            )

            return response.text

        except Exception as exc:

            if self._is_quota_error(exc):
                raise GeminiQuotaExceededError(
                    str(exc)
                ) from exc

            raise

    def generate_json(
        self,
        prompt: str,
        schema: dict,
    ) -> dict:

        self._acquire_request()

        try:

            response = (
                self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type=(
                            "application/json"
                        ),
                        response_schema=schema,
                    ),
                )
            )

            return response.parsed

        except Exception as exc:

            if self._is_quota_error(exc):
                raise GeminiQuotaExceededError(
                    str(exc)
                ) from exc

            raise

    @staticmethod
    def _is_quota_error(
        exc: Exception,
    ) -> bool:

        message = str(exc).lower()

        return (
            "resource_exhausted" in message
            or "quota exceeded" in message
            or "429" in message
        )