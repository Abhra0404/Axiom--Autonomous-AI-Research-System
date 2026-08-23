import json

import ollama

from app.core.llm import LLMProvider


class OllamaProvider(LLMProvider):

    def __init__(self, model: str = "qwen3:8b"):
        self.model = model

    def generate(self, prompt: str) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response["message"]["content"]

    def generate_json(self, prompt: str) -> dict:
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            format="json",
        )

        return json.loads(response["message"]["content"])