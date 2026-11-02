from typing import Literal

from app.config import Settings
from app.models.schemas import AIInsightsRequest, AIInsightsResponse
from app.services.ai.context_builder import build_insights_context, context_to_prompt_json
from app.services.ai.gemini_client import InsightGenerator, build_generator
from app.services.ai.validation import find_unsupported_numbers
from app.services.data_loader import ProcessedDataStore

AIStatus = Literal["ok", "unavailable", "validation_warning", "error"]

FALLBACK_NO_KEY = (
    "AI insights are temporarily unavailable because the Gemini API key is not configured. "
    "You can still use the venue, player and comparison statistics shown in the evidence panel."
)
FALLBACK_ERROR = (
    "AI insights could not be generated right now. Please rely on the supplied statistics below "
    "and try again later."
)


def _safe_error_message(exc: Exception) -> str:
    from google.genai import errors as genai_errors

    if isinstance(exc, genai_errors.APIError):
        code = getattr(exc, "code", None)
        if code == 429:
            return (
                "Gemini free-tier daily quota is used up (429). "
                "Wait until it resets (~hours), enable billing in Google AI Studio, "
                "or use a new API key. Venue/Players/Compare still work without AI."
            )
        if code == 503:
            return "Gemini is busy (503). Wait a minute and try again."
        if code == 504:
            return "Gemini timed out (504). Try again or increase GEMINI_TIMEOUT_MS."
        if code in {401, 403}:
            return "Gemini rejected the API key (401/403). Check GEMINI_API_KEY in backend/.env."
        return f"Gemini API error ({code}): {exc}"
    return f"AI service error: {type(exc).__name__}: {exc}"


def generate_ai_insights(
    store: ProcessedDataStore,
    settings: Settings,
    body: AIInsightsRequest,
    generator: InsightGenerator | None = None,
) -> AIInsightsResponse:
    question = body.question.strip()
    if not question:
        raise ValueError("Question cannot be empty")
    if len(question) > settings.ai_max_question_length:
        raise ValueError(f"Question exceeds maximum length of {settings.ai_max_question_length} characters")

    evidence = build_insights_context(
        store,
        body.match_id,
        body.player_a_id,
        body.player_b_id,
    )
    stats_json = context_to_prompt_json(evidence)

    gen = generator
    if gen is None:
        gen = build_generator(
            settings.gemini_api_key,
            settings.gemini_model,
            settings.gemini_timeout_ms,
        )

    if gen is None:
        return AIInsightsResponse(
            status="unavailable",
            answer=FALLBACK_NO_KEY,
            evidence=evidence,
            notes=["Set GEMINI_API_KEY in backend/.env to enable AI insights."],
        )

    try:
        answer = gen.generate(question, stats_json)
    except Exception as exc:
        detail = _safe_error_message(exc)
        return AIInsightsResponse(
            status="error",
            answer=FALLBACK_ERROR,
            evidence=evidence,
            notes=[detail, "Historical statistics remain available in View stats."],
        )

    unsupported = find_unsupported_numbers(answer, evidence)
    status: AIStatus = "ok"
    notes: list[str] = []
    if unsupported:
        status = "validation_warning"
        notes.append(
            "The AI response may contain numbers not present in the supplied statistics: "
            + ", ".join(sorted(set(unsupported))[:8])
        )

    return AIInsightsResponse(
        status=status,
        answer=answer,
        evidence=evidence,
        notes=notes,
    )
