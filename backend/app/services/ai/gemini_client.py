from typing import Protocol

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.services.ai.prompts import SYSTEM_INSTRUCTION


class InsightGenerator(Protocol):
    def generate(self, question: str, stats_json: str) -> str: ...


class GeminiInsightGenerator:
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-3.8-flash",
        timeout_ms: int = 120_000,
    ) -> None:
        self._model = model_name
        self._client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=timeout_ms),
        )

    def generate(self, question: str, stats_json: str) -> str:
        prompt = (
            "Answer the user question using ONLY the statistics below.\n\n"
            f"USER QUESTION:\n{question}\n\n"
            f"STATISTICS JSON:\n{stats_json}\n"
        )
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.4,
            max_output_tokens=512,
        )
        response = None
        last_error: Exception | None = None
        for _ in range(2):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=prompt,
                    config=config,
                )
                break
            except genai_errors.ServerError as exc:
                last_error = exc
                if exc.code not in {503, 504}:
                    raise
        if response is None:
            raise last_error or RuntimeError("Gemini request failed")
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Empty response from Gemini")
        return text


def build_generator(
    api_key: str,
    model_name: str,
    timeout_ms: int = 120_000,
) -> InsightGenerator | None:
    if not api_key.strip():
        return None
    return GeminiInsightGenerator(
        api_key=api_key,
        model_name=model_name,
        timeout_ms=timeout_ms,
    )
