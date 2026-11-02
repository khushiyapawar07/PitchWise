import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.data_loader import reset_data_store_cache

client = TestClient(app)

DEMO_MATCH = "1426267"
RG_SHARMA = "740742ef"
SA_YADAV = "271f83cd"
JJ_BUMRAH = "462411b3"


@pytest.fixture(autouse=True)
def _fresh_store() -> None:
    reset_data_store_cache()


def test_compare_two_batters() -> None:
    response = client.post(
        "/api/compare",
        json={
            "player_a_id": RG_SHARMA,
            "player_b_id": SA_YADAV,
            "match_id": DEMO_MATCH,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["player_a"]["player_name"] == "RG Sharma"
    assert body["player_b"]["player_name"] == "SA Yadav"
    assert body["context"]["as_of_date"] == "2024-04-13"
    assert len(body["metrics"]) >= 5
    venue_row = next(m for m in body["metrics"] if m["metric_key"] == "venue_batting_average")
    assert venue_row["player_a"]["sample_size"] >= 0
    assert venue_row["player_b"]["sample_size"] >= 0
    if venue_row["player_a"]["value"] is not None and venue_row["player_b"]["value"] is not None:
        assert venue_row["difference"] is not None


def test_compare_same_player_rejected() -> None:
    response = client.post(
        "/api/compare",
        json={
            "player_a_id": RG_SHARMA,
            "player_b_id": RG_SHARMA,
            "match_id": DEMO_MATCH,
        },
    )
    assert response.status_code == 400


def test_compare_unknown_player_404() -> None:
    response = client.post(
        "/api/compare",
        json={
            "player_a_id": RG_SHARMA,
            "player_b_id": "00000000",
            "match_id": DEMO_MATCH,
        },
    )
    assert response.status_code == 404


def test_compare_missing_metric_no_fabricated_difference() -> None:
    response = client.post(
        "/api/compare",
        json={
            "player_a_id": RG_SHARMA,
            "player_b_id": JJ_BUMRAH,
            "match_id": DEMO_MATCH,
        },
    )
    assert response.status_code == 200
    venue_row = next(
        m for m in response.json()["metrics"] if m["metric_key"] == "venue_batting_average"
    )
    if venue_row["player_a"]["value"] is None or venue_row["player_b"]["value"] is None:
        assert venue_row["difference"] is None


def test_compare_cutoff_in_context() -> None:
    response = client.post(
        "/api/compare",
        json={
            "player_a_id": RG_SHARMA,
            "player_b_id": SA_YADAV,
            "match_id": DEMO_MATCH,
        },
    )
    assert response.json()["context"]["as_of_date"] == "2024-04-13"
