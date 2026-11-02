from statistics import mean

from app.models.schemas import (
    Availability,
    CompareMetricRow,
    ComparePlayersRequest,
    ComparePlayersResponse,
    ComparePlayerSummary,
    CompareSideMetric,
    DataContextMeta,
    PlayerMetricBlock,
    PlayerStatsResponse,
)
from app.services.data_loader import ProcessedDataStore
from app.services.stats.player import compute_player_stats


def _recent_batting_average(stats: PlayerStatsResponse) -> tuple[float | None, int]:
    runs = [i.runs for i in stats.recent_batting if i.runs is not None]
    if not runs:
        return None, 0
    return round(mean(runs), 2), len(runs)


def _recent_bowling_wickets_avg(stats: PlayerStatsResponse) -> tuple[float | None, int]:
    wkts = [i.wickets for i in stats.recent_bowling if i.wickets is not None]
    if not wkts:
        return None, 0
    return round(mean(wkts), 2), len(wkts)


def _side(
    stats: PlayerStatsResponse,
    value: float | None,
    sample_size: int,
    availability: Availability,
) -> CompareSideMetric:
    return CompareSideMetric(
        player_id=stats.player_id,
        player_name=stats.player_name,
        value=value,
        sample_size=sample_size,
        availability=availability,
    )


def _row_from_block(
    key: str,
    label: str,
    stats_a: PlayerStatsResponse,
    stats_b: PlayerStatsResponse,
    block_a: PlayerMetricBlock,
    block_b: PlayerMetricBlock,
    field: str,
) -> CompareMetricRow:
    val_a = getattr(block_a, field)
    val_b = getattr(block_b, field)
    sample_a = block_a.sample_size_innings
    sample_b = block_b.sample_size_innings
    diff = None
    if val_a is not None and val_b is not None:
        diff = round(float(val_a) - float(val_b), 2)
    return CompareMetricRow(
        metric_key=key,
        label=label,
        player_a=_side(stats_a, val_a, sample_a, block_a.availability),
        player_b=_side(stats_b, val_b, sample_b, block_b.availability),
        difference=diff,
    )


def _row_from_values(
    key: str,
    label: str,
    stats_a: PlayerStatsResponse,
    stats_b: PlayerStatsResponse,
    val_a: float | None,
    sample_a: int,
    avail_a: Availability,
    val_b: float | None,
    sample_b: int,
    avail_b: Availability,
) -> CompareMetricRow:
    diff = None
    if val_a is not None and val_b is not None:
        diff = round(val_a - val_b, 2)
    return CompareMetricRow(
        metric_key=key,
        label=label,
        player_a=_side(stats_a, val_a, sample_a, avail_a),
        player_b=_side(stats_b, val_b, sample_b, avail_b),
        difference=diff,
    )


def _summary(stats: PlayerStatsResponse) -> ComparePlayerSummary:
    venue_avg = stats.venue_batting.average
    return ComparePlayerSummary(
        player_id=stats.player_id,
        player_name=stats.player_name,
        team=stats.team,
        playing_role=stats.playing_role,
        venue_batting_average=venue_avg,
        venue_batting_sample_size=stats.venue_batting.sample_size_innings,
    )


def compare_players(
    store: ProcessedDataStore,
    body: ComparePlayersRequest,
) -> ComparePlayersResponse:
    if body.player_a_id == body.player_b_id:
        raise ValueError("Cannot compare a player with themselves")

    if store.demo.get_match(body.match_id) is None:
        raise KeyError(f"Unknown match_id: {body.match_id}")

    cutoff = store.demo.cutoff()
    stats_a = compute_player_stats(store, body.match_id, body.player_a_id, cutoff)
    stats_b = compute_player_stats(store, body.match_id, body.player_b_id, cutoff)

    recent_avg_a, recent_n_a = _recent_batting_average(stats_a)
    recent_avg_b, recent_n_b = _recent_batting_average(stats_b)
    from app.services.stats.availability import availability_from_sample

    recent_avail_a = availability_from_sample(recent_n_a)
    recent_avail_b = availability_from_sample(recent_n_b)

    bowl_recent_a, bowl_n_a = _recent_bowling_wickets_avg(stats_a)
    bowl_recent_b, bowl_n_b = _recent_bowling_wickets_avg(stats_b)

    metrics: list[CompareMetricRow] = [
        _row_from_values(
            "recent_batting_average",
            "Recent batting average (last up to 5 innings)",
            stats_a,
            stats_b,
            recent_avg_a,
            recent_n_a,
            recent_avail_a,
            recent_avg_b,
            recent_n_b,
            recent_avail_b,
        ),
        _row_from_block(
            "venue_batting_average",
            "Venue batting average",
            stats_a,
            stats_b,
            stats_a.venue_batting,
            stats_b.venue_batting,
            "average",
        ),
        _row_from_block(
            "venue_batting_strike_rate",
            "Venue batting strike rate",
            stats_a,
            stats_b,
            stats_a.venue_batting,
            stats_b.venue_batting,
            "strike_rate",
        ),
        _row_from_block(
            "opponent_batting_average",
            "Batting average vs opposition",
            stats_a,
            stats_b,
            stats_a.opponent_batting,
            stats_b.opponent_batting,
            "average",
        ),
        _row_from_block(
            "venue_bowling_economy",
            "Venue bowling economy",
            stats_a,
            stats_b,
            stats_a.venue_bowling,
            stats_b.venue_bowling,
            "economy",
        ),
        _row_from_block(
            "venue_bowling_wickets",
            "Venue bowling wickets per innings",
            stats_a,
            stats_b,
            stats_a.venue_bowling,
            stats_b.venue_bowling,
            "wickets",
        ),
        _row_from_values(
            "recent_bowling_wickets",
            "Recent bowling wickets per innings (last up to 5)",
            stats_a,
            stats_b,
            bowl_recent_a,
            bowl_n_a,
            availability_from_sample(bowl_n_a),
            bowl_recent_b,
            bowl_n_b,
            availability_from_sample(bowl_n_b),
        ),
    ]

    context = DataContextMeta(
        as_of_date=cutoff.as_of_date.isoformat(),
        rules_version=str(store.manifest.get("rules_version") or "1.0.0"),
    )

    notes = [
        "Positive difference favours Player A over Player B for this metric.",
        "Unavailable metrics are omitted from difference calculations.",
        "Historical window excludes the selected match and fixtures after the cutoff.",
    ]

    return ComparePlayersResponse(
        match_id=body.match_id,
        context=context,
        player_a=_summary(stats_a),
        player_b=_summary(stats_b),
        metrics=metrics,
        notes=notes,
    )
