import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.delivery_stats import (
    MatchDeliveryStats,
    collect_innings_deliveries,
    innings_total_runs,
    innings_total_wickets,
)
from app.services.match_classification import (
    classify_result,
    counts_for_venue_regulation_innings_averages,
    counts_for_win_percentage,
    match_winner,
)
from app.utils.venues import load_venue_alias_map, normalize_venue

RULES_VERSION = "1.0.0"


@dataclass
class InningsSummary:
    team: str
    is_super_over: bool
    runs: int
    wickets: int
    regulation_innings_index: int | None


@dataclass
class PlayerPerformanceRow:
    player_name: str
    person_id: str | None
    team: str | None
    runs: int | None
    balls_faced: int | None
    wickets: int | None
    runs_conceded: int | None
    legal_balls_bowled: int | None


def _person_registry(info: dict) -> dict[str, str]:
    return (info.get("registry") or {}).get("people") or {}


def _team_for_player(info: dict, player_name: str) -> str | None:
    squads = info.get("players") or {}
    for team, names in squads.items():
        if player_name in names:
            return team
    return None


def parse_match_file(path: Path, alias_map: dict[str, str]) -> dict[str, Any]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    info = doc["info"]
    match_id = path.stem
    match_date = (info.get("dates") or [None])[0]
    raw_venue = info.get("venue")
    venue_id = normalize_venue(raw_venue, alias_map)
    result_type = classify_result(info)
    registry = _person_registry(info)

    innings_summaries: list[InningsSummary] = []
    regulation_index = 0
    all_performances: list[PlayerPerformanceRow] = []

    for innings in doc.get("innings") or []:
        is_super = bool(innings.get("super_over"))
        deliveries = collect_innings_deliveries(innings)
        runs = innings_total_runs(deliveries)
        wickets = innings_total_wickets(deliveries)
        reg_idx: int | None = None
        if not is_super:
            regulation_index += 1
            reg_idx = regulation_index

        innings_summaries.append(
            InningsSummary(
                team=innings["team"],
                is_super_over=is_super,
                runs=runs,
                wickets=wickets,
                regulation_innings_index=reg_idx,
            )
        )

        stats = MatchDeliveryStats()
        for delivery in deliveries:
            stats.process_delivery(delivery)

        batting_team = innings["team"]
        for player_name, acc in stats.players.items():
            team = _team_for_player(info, player_name) or batting_team
            all_performances.append(
                PlayerPerformanceRow(
                    player_name=player_name,
                    person_id=registry.get(player_name),
                    team=team,
                    runs=acc.runs if acc.batted else None,
                    balls_faced=acc.balls_faced if acc.batted else None,
                    wickets=acc.wickets if acc.bowled else None,
                    runs_conceded=acc.runs_conceded if acc.bowled else None,
                    legal_balls_bowled=acc.legal_balls_bowled if acc.bowled else None,
                )
            )

    toss = info.get("toss") or {}
    teams = info.get("teams") or []

    return {
        "match_id": match_id,
        "match_date": match_date,
        "match_format": info.get("match_type"),
        "event_name": (info.get("event") or {}).get("name"),
        "teams": teams,
        "squads": info.get("players") or {},
        "player_registry": registry,
        "venue_raw": raw_venue,
        "venue_id": venue_id,
        "city": info.get("city"),
        "toss_winner": toss.get("winner"),
        "toss_decision": toss.get("decision"),
        "match_winner": match_winner(info),
        "result_type": result_type,
        "counts_for_win_percentage": counts_for_win_percentage(result_type),
        "counts_for_venue_regulation_innings_averages": counts_for_venue_regulation_innings_averages(
            result_type
        ),
        "innings": [asdict(i) for i in innings_summaries],
        "performances": [asdict(p) for p in all_performances],
    }


def build_processed_dataset(
    raw_dir: Path,
    metadata_venues_path: Path,
    processed_dir: Path,
) -> dict[str, Any]:
    alias_map = load_venue_alias_map(metadata_venues_path)
    raw_files = sorted(raw_dir.glob("*.json"))
    matches: list[dict[str, Any]] = []
    performances_by_match: dict[str, list[dict[str, Any]]] = {}
    unknown_venues: set[str] = set()

    for path in raw_files:
        row = parse_match_file(path, alias_map)
        if row["venue_id"] is None and row["venue_raw"]:
            unknown_venues.add(row["venue_raw"])
        perf = row.pop("performances")
        performances_by_match[row["match_id"]] = perf
        matches.append(row)

    manifest = {
        "rules_version": RULES_VERSION,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source": "Cricsheet IPL JSON",
        "raw_match_count": len(raw_files),
        "unknown_venue_strings": sorted(unknown_venues),
    }

    processed_dir.mkdir(parents=True, exist_ok=True)
    (processed_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    (processed_dir / "matches.json").write_text(
        json.dumps(matches, indent=2), encoding="utf-8"
    )
    (processed_dir / "performances_by_match.json").write_text(
        json.dumps(performances_by_match, indent=2), encoding="utf-8"
    )

    return manifest
