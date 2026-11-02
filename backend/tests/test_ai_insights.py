import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app
from app.services.ai.insights import generate_ai_insights
from app.services.data_loader import ProcessedDataStore, reset_data_store_cache
from app.models.schemas import AIInsightsRequest

client = TestClient(app)

DEMO_MATCH = "1426267"
RG_SHARMA = "740742ef"
SA_YADAV = "271f83cd"


class FakeGenerator:
    def __init__(self, answer: str) -> None:
        self.answer = answer
        self.last_stats: str | None = None

    def generate(self, question: str, stats_json: str) -> str:
        self.last_stats = stats_json
        return self.answer


@pytest.fixture(autouse=True)
def _fresh_store() -> None:
    reset_data_store_cache()


def test_ai_unavailable_without_api_key() -> None:
    empty = Settings(gemini_api_key="").resolve_paths()
    app.dependency_overrides[get_settings] = lambda: empty
    response = client.post(
        "/api/ai/insights",
        json={
            "question": "Who has the better venue record?",
            "match_id": DEMO_MATCH,
            "player_a_id": RG_SHARMA,
            "player_b_id": SA_YADAV,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "unavailable"
    assert "evidence" in body
    assert body["evidence"]["match"]["match_id"] == DEMO_MATCH
    assert body["evidence"]["comparison"] is not None
    app.dependency_overrides.clear()


def test_ai_with_mock_generator_uses_evidence() -> None:
    store = ProcessedDataStore(get_settings())
    settings = Settings(gemini_api_key="test-key", gemini_timeout_ms=120000).resolve_paths()
    fake = FakeGenerator("Both players have historical records at this venue with limited samples.")
    result = generate_ai_insights(
        store,
        settings,
        AIInsightsRequest(
            question="Compare venue form",
            match_id=DEMO_MATCH,
            player_a_id=RG_SHARMA,
            player_b_id=SA_YADAV,
        ),
        generator=fake,
    )
    assert result.status == "ok"
    assert fake.last_stats is not None
    assert "venue" in fake.last_stats
    assert RG_SHARMA in fake.last_stats or "RG Sharma" in fake.last_stats


def test_ai_validation_warning_on_invented_number() -> None:
    store = ProcessedDataStore(get_settings())
    settings = Settings(gemini_api_key="test-key", gemini_timeout_ms=120000).resolve_paths()
    fake = FakeGenerator("Player A averages 9999.9 at this venue.")
    result = generate_ai_insights(
        store,
        settings,
        AIInsightsRequest(
            question="Venue average?",
            match_id=DEMO_MATCH,
            player_a_id=RG_SHARMA,
        ),
        generator=fake,
    )
    assert result.status == "validation_warning"
    assert any("9999" in n or "unsupported" in n.lower() for n in result.notes)


def test_ai_question_length_limit() -> None:
    response = client.post(
        "/api/ai/insights",
        json={
            "question": "x" * 501,
            "match_id": DEMO_MATCH,
        },
    )
    assert response.status_code == 400


def test_ai_api_error_fallback() -> None:
    store = ProcessedDataStore(get_settings())
    settings = Settings(gemini_api_key="test-key", gemini_timeout_ms=120000).resolve_paths()

    class BrokenGenerator:
        def generate(self, question: str, stats_json: str) -> str:
            raise RuntimeError("network down")

    result = generate_ai_insights(
        store,
        settings,
        AIInsightsRequest(question="Help", match_id=DEMO_MATCH),
        generator=BrokenGenerator(),
    )
    assert result.status == "error"
    assert result.evidence["venue_stats"] is not None
