import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.data_loader import reset_data_store_cache

client = TestClient(app)

DEMO_MATCH = "1426267"
VENUE = "wankhede_mumbai"
RG_SHARMA = "740742ef"


@pytest.fixture(autouse=True)
def _fresh_store() -> None:
    reset_data_store_cache()


def test_list_demo_matches() -> None:
    response = client.get("/api/matches")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["match_id"] == DEMO_MATCH


def test_match_detail_includes_cutoff() -> None:
    response = client.get(f"/api/matches/{DEMO_MATCH}")
    assert response.status_code == 200
    body = response.json()
    assert body["historical_cutoff_date"] == "2024-04-13"
    assert body["venue_id"] == VENUE


def test_venue_stats_wankhede_historical_count() -> None:
    response = client.get(
        f"/api/venues/{VENUE}/stats",
        params={"match_id": DEMO_MATCH},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_matches_analysed"] == 114
    assert body["context"]["as_of_date"] == "2024-04-13"
    assert body["average_first_innings_score"]["sample_size"] > 0
    assert "1426267" not in str(body)


def test_venue_stats_cutoff_leakage_excludes_demo_date() -> None:
    response = client.get(
        f"/api/venues/{VENUE}/stats",
        params={"match_id": DEMO_MATCH},
    )
    assert response.status_code == 200
    assert response.json()["total_matches_analysed"] < 132


def test_players_list_for_demo_match() -> None:
    response = client.get("/api/players", params={"match_id": DEMO_MATCH})
    assert response.status_code == 200
    players = response.json()
    assert len(players) >= 22
    names = {p["player_name"] for p in players}
    assert "RG Sharma" in names


def test_player_stats_rg_sharma() -> None:
    response = client.get(
        f"/api/players/{RG_SHARMA}/stats",
        params={"match_id": DEMO_MATCH},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["player_name"] == "RG Sharma"
    assert body["context"]["as_of_date"] == "2024-04-13"
    assert body["venue_batting"]["availability"] in {"sufficient", "limited", "unavailable"}


def test_unknown_venue_returns_404() -> None:
    response = client.get(
        "/api/venues/unknown_venue/stats",
        params={"match_id": DEMO_MATCH},
    )
    assert response.status_code == 404
