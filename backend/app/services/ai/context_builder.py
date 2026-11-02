import json
from typing import Any

from app.models.schemas import ComparePlayersRequest
from app.services.data_loader import ProcessedDataStore
from app.services.stats.compare import compare_players
from app.services.stats.player import compute_player_stats
from app.services.stats.venue import compute_venue_stats


def build_insights_context(
    store: ProcessedDataStore,
    match_id: str,
    player_a_id: str | None,
    player_b_id: str | None,
) -> dict[str, Any]:
    demo = store.demo.get_match(match_id)
    if demo is None:
        raise KeyError(f"Unknown match_id: {match_id}")

    cutoff = store.demo.cutoff()
    venue = store.venue_record(demo["venue_id"])

    payload: dict[str, Any] = {
        "data_source": "Cricsheet IPL JSON",
        "as_of_date": cutoff.as_of_date.isoformat(),
        "rules_version": store.manifest.get("rules_version"),
        "match": {
            "match_id": match_id,
            "display_title": demo.get("display_title"),
            "team_1": demo["team_1"],
            "team_2": demo["team_2"],
            "venue_id": demo["venue_id"],
            "venue_name": (venue or {}).get("venue_name"),
            "match_date": demo["match_date"],
            "historical_cutoff_date": store.demo.historical_cutoff_date,
            "note": "Statistics exclude this match and later fixtures.",
        },
        "venue_stats": compute_venue_stats(store, demo["venue_id"], cutoff).model_dump(),
        "players": [],
        "comparison": None,
    }

    if player_a_id:
        payload["players"].append(
            compute_player_stats(store, match_id, player_a_id, cutoff).model_dump()
        )
    if player_b_id and player_b_id != player_a_id:
        payload["players"].append(
            compute_player_stats(store, match_id, player_b_id, cutoff).model_dump()
        )

    if player_a_id and player_b_id and player_a_id != player_b_id:
        payload["comparison"] = compare_players(
            store,
            ComparePlayersRequest(
                player_a_id=player_a_id,
                player_b_id=player_b_id,
                match_id=match_id,
            ),
        ).model_dump()

    return payload


def compact_context_for_gemini(full: dict[str, Any]) -> dict[str, Any]:
    """Smaller payload for Gemini — faster responses, same numbers as evidence."""
    venue = full.get("venue_stats") or {}
    compact: dict[str, Any] = {
        "data_source": full.get("data_source"),
        "as_of_date": full.get("as_of_date"),
        "match": full.get("match"),
        "venue": {
            "total_matches_analysed": venue.get("total_matches_analysed"),
            "average_first_innings_score": _metric_key(venue, "average_first_innings_score"),
            "average_second_innings_score": _metric_key(venue, "average_second_innings_score"),
            "batting_first_win_percentage": _metric_key(venue, "batting_first_win_percentage"),
            "chasing_win_percentage": _metric_key(venue, "chasing_win_percentage"),
        },
        "players": [],
        "comparison_metrics": [],
    }

    for p in full.get("players") or []:
        compact["players"].append(
            {
                "player_id": p.get("player_id"),
                "player_name": p.get("player_name"),
                "team": p.get("team"),
                "recent_batting": (p.get("recent_batting") or [])[:5],
                "venue_batting": p.get("venue_batting"),
                "opponent_batting": p.get("opponent_batting"),
                "venue_bowling": p.get("venue_bowling"),
            }
        )

    comparison = full.get("comparison") or {}
    for row in comparison.get("metrics") or []:
        compact["comparison_metrics"].append(
            {
                "label": row.get("label"),
                "player_a": row.get("player_a"),
                "player_b": row.get("player_b"),
                "difference": row.get("difference"),
            }
        )

    return compact


def _metric_key(venue: dict[str, Any], key: str) -> dict[str, Any]:
    block = venue.get(key) or {}
    return {
        "value": block.get("value"),
        "sample_size": block.get("sample_size"),
        "availability": block.get("availability"),
    }


def context_to_prompt_json(context: dict[str, Any], *, compact: bool = True) -> str:
    payload = compact_context_for_gemini(context) if compact else context
    return json.dumps(payload, separators=(",", ":"), default=str)
