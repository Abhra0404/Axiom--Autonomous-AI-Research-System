import os

from google import genai
from google.genai import types

from app.core.llm import LLMProvider
from app.core.retry import retry


class GeminiProvider(LLMProvider):

    def __init__(self, model: str | None = None):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured"
            )

        self.client = genai.Client(api_key=api_key)

        self.model = model or os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash",
        )

    def generate(self, prompt: str) -> str:

        def request():
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            return response.text

        return retry(request)

    def generate_json(
        self,
        prompt: str,
        schema: dict,
    ) -> dict:

        def request():

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )

            return response.parsed

        return retry(request)