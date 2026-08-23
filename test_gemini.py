from dotenv import load_dotenv

from app.core.gemini_llm import GeminiProvider


load_dotenv()


llm = GeminiProvider()

response = llm.generate(
    "Explain Retrieval-Augmented Generation in three sentences."
)

print("\n=== GEMINI RESPONSE ===\n")
print(response)