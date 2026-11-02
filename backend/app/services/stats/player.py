from statistics import mean
from typing import Any

from app.models.schemas import (
    DataContextMeta,
    PlayerInningsSummary,
    PlayerListItem,
    PlayerMetricBlock,
    PlayerStatsResponse,
)
from app.services.data_loader import ProcessedDataStore
from app.services.stats.availability import availability_from_sample
from app.utils.cutoff import CutoffContext

RECENT_LIMIT = 5


def _opponent_for_team(match: dict[str, Any], team: str) -> str | None:
    teams = match.get("teams") or []
    for t in teams:
        if t != team:
            return t
    return None


def _strike_rate(runs: int | None, balls: int | None) -> float | None:
    if runs is None or balls is None or balls == 0:
        return None
    return round(100.0 * runs / balls, 2)


def _economy(runs_conceded: int | None, legal_balls: int | None) -> float | None:
    if runs_conceded is None or legal_balls is None or legal_balls == 0:
        return None
    return round(runs_conceded / (legal_balls / 6.0), 2)


def list_players_for_match(store: ProcessedDataStore, match_id: str) -> list[PlayerListItem]:
    demo = store.demo.get_match(match_id)
    if demo is None:
        raise KeyError(f"Unknown match_id: {match_id}")

    processed = store.match_by_id(match_id)
    squads = (processed or {}).get("squads") or {}
    items: list[PlayerListItem] = []

    registry = (processed or {}).get("player_registry") or {}
    for team, names in squads.items():
        for name in names:
            person_id = registry.get(name)
            meta = store.player_metadata(person_id)
            if not person_id:
                raise KeyError(f"Missing registry id for {name} in match {match_id}")
            items.append(
                PlayerListItem(
                    player_id=person_id,
                    player_name=name,
                    team=team,
                    playing_role=meta["playing_role"],
                    batting_style=meta["batting_style"],
                    bowling_style=meta["bowling_style"],
                )
            )
    return sorted(items, key=lambda p: (p.team, p.player_name))


def _resolve_player_name(store: ProcessedDataStore, match_id: str, player_id: str) -> tuple[str, str]:
    for item in list_players_for_match(store, match_id):
        if item.player_id == player_id:
            return item.player_name, item.team
    raise KeyError(f"Unknown player_id {player_id} for match {match_id}")


def _collect_player_innings(
    store: ProcessedDataStore,
    player_name: str,
    cutoff: CutoffContext,
    *,
    venue_id: str | None = None,
    opponent: str | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for match in store.matches:
        mid = match["match_id"]
        mdate = match.get("match_date")
        if not mdate or not cutoff.includes_match(mid, mdate):
            continue
        if venue_id and match.get("venue_id") != venue_id:
            continue
        perf = None
        for p in store.performances_by_match.get(mid, []):
            if p["player_name"] == player_name:
                perf = p
                break
        if perf is None:
            continue
        team = perf.get("team")
        if opponent and _opponent_for_team(match, team or "") != opponent:
            continue
        rows.append({"match": match, "perf": perf})
    rows.sort(key=lambda r: r["match"]["match_date"], reverse=True)
    return rows


def _batting_block(innings_rows: list[dict[str, Any]]) -> PlayerMetricBlock:
    scores = [r["perf"]["runs"] for r in innings_rows if r["perf"].get("runs") is not None]
    balls = [r["perf"]["balls_faced"] for r in innings_rows if r["perf"].get("balls_faced") is not None]
    if not scores:
        return PlayerMetricBlock(sample_size_innings=0, availability="unavailable")
    srs = [
        _strike_rate(r["perf"]["runs"], r["perf"]["balls_faced"])
        for r in innings_rows
        if r["perf"].get("runs") is not None and r["perf"].get("balls_faced") is not None
    ]
    srs_valid = [s for s in srs if s is not None]
    return PlayerMetricBlock(
        average=round(mean(scores), 2),
        strike_rate=round(mean(srs_valid), 2) if srs_valid else None,
        sample_size_innings=len(scores),
        availability=availability_from_sample(len(scores)),
    )


def _bowling_block(innings_rows: list[dict[str, Any]]) -> PlayerMetricBlock:
    wicket_rows = [r for r in innings_rows if r["perf"].get("wickets") is not None]
    if not wicket_rows:
        return PlayerMetricBlock(sample_size_innings=0, availability="unavailable")
    wickets = [int(r["perf"]["wickets"] or 0) for r in wicket_rows]
    economies = [
        _economy(r["perf"].get("runs_conceded"), r["perf"].get("legal_balls_bowled"))
        for r in wicket_rows
    ]
    eco_valid = [e for e in economies if e is not None]
    return PlayerMetricBlock(
        wickets=round(mean(wickets), 2),
        economy=round(mean(eco_valid), 2) if eco_valid else None,
        sample_size_innings=len(wicket_rows),
        availability=availability_from_sample(len(wicket_rows)),
    )


def _recent_summaries(innings_rows: list[dict[str, Any]], limit: int, batting: bool) -> list[PlayerInningsSummary]:
    out: list[PlayerInningsSummary] = []
    for row in innings_rows[:limit]:
        match = row["match"]
        perf = row["perf"]
        team = perf.get("team") or ""
        opponent = _opponent_for_team(match, team) or "unknown"
        if batting and perf.get("runs") is None:
            continue
        if not batting and perf.get("wickets") is None:
            continue
        out.append(
            PlayerInningsSummary(
                match_id=match["match_id"],
                match_date=match["match_date"],
                opponent=opponent,
                runs=perf.get("runs"),
                balls_faced=perf.get("balls_faced"),
                strike_rate=_strike_rate(perf.get("runs"), perf.get("balls_faced")),
                wickets=perf.get("wickets"),
                runs_conceded=perf.get("runs_conceded"),
                legal_balls_bowled=perf.get("legal_balls_bowled"),
                economy=_economy(perf.get("runs_conceded"), perf.get("legal_balls_bowled")),
            )
        )
    return out


def compute_player_stats(
    store: ProcessedDataStore,
    match_id: str,
    player_id: str,
    cutoff: CutoffContext,
) -> PlayerStatsResponse:
    demo_match = store.demo.get_match(match_id)
    if demo_match is None:
        raise KeyError(f"Unknown match_id: {match_id}")

    player_name, team = _resolve_player_name(store, match_id, player_id)
    venue_id = demo_match["venue_id"]
    opponent = _opponent_for_team(
        {"teams": [demo_match["team_1"], demo_match["team_2"]]},
        team,
    )

    all_innings = _collect_player_innings(store, player_name, cutoff)
    venue_innings = _collect_player_innings(store, player_name, cutoff, venue_id=venue_id)
    opponent_innings = _collect_player_innings(store, player_name, cutoff, opponent=opponent)

    meta = store.player_metadata(player_id)

    context = DataContextMeta(
        as_of_date=cutoff.as_of_date.isoformat(),
        rules_version=str(store.manifest.get("rules_version") or "1.0.0"),
    )

    return PlayerStatsResponse(
        player_id=player_id,
        player_name=player_name,
        team=team,
        playing_role=meta["playing_role"],
        batting_style=meta["batting_style"],
        bowling_style=meta["bowling_style"],
        context=context,
        recent_batting=_recent_summaries(all_innings, RECENT_LIMIT, batting=True),
        recent_bowling=_recent_summaries(all_innings, RECENT_LIMIT, batting=False),
        venue_batting=_batting_block(venue_innings),
        venue_bowling=_bowling_block(venue_innings),
        opponent_batting=_batting_block(opponent_innings),
        opponent_bowling=_bowling_block(opponent_innings),
        notes=[
            "Historical stats exclude the selected match and any fixtures after the cutoff date.",
            "Missing innings are omitted, not treated as zero.",
        ],
    )
