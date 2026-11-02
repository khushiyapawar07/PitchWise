from statistics import mean
from typing import Any

from app.models.schemas import DataContextMeta, MetricWithSample, VenueStatsResponse
from app.services.data_loader import ProcessedDataStore
from app.services.stats.availability import availability_from_sample
from app.utils.cutoff import CutoffContext

RULES_NOTES = [
    "Regulation innings exclude super overs.",
    "No-result matches excluded from venue innings averages and win-percentage denominators.",
    "Tied matches excluded from win-percentage denominators only.",
    "DLS/shortened innings use ball-by-ball totals recorded in Cricsheet.",
]


def _regulation_innings(match: dict[str, Any]) -> list[dict[str, Any]]:
    return [inn for inn in match.get("innings") or [] if not inn.get("is_super_over")]


def _historical_matches(
    store: ProcessedDataStore,
    venue_id: str,
    cutoff: CutoffContext,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for match in store.matches:
        if match.get("venue_id") != venue_id:
            continue
        match_id = match["match_id"]
        match_date = match.get("match_date")
        if not match_date or not cutoff.includes_match(match_id, match_date):
            continue
        out.append(match)
    return out


def _metric(value: float | int | None, sample: int, label: str | None = None) -> MetricWithSample:
    return MetricWithSample(
        value=round(value, 2) if isinstance(value, float) else value,
        sample_size=sample,
        availability=availability_from_sample(sample),
        label=label,
    )


def compute_venue_stats(
    store: ProcessedDataStore,
    venue_id: str,
    cutoff: CutoffContext,
) -> VenueStatsResponse:
    venue = store.venue_record(venue_id)
    if venue is None:
        raise KeyError(f"Unknown venue_id: {venue_id}")

    historical = _historical_matches(store, venue_id, cutoff)
    first_scores: list[int] = []
    second_scores: list[int] = []
    all_regulation_totals: list[int] = []
    bat_first_wins = 0
    chase_wins = 0
    win_eligible = 0

    pace_wkts = spin_wkts = unknown_wkts = 0

    for match in historical:
        if match.get("counts_for_venue_regulation_innings_averages"):
            reg = _regulation_innings(match)
            if len(reg) >= 1:
                first_scores.append(int(reg[0]["runs"]))
                all_regulation_totals.append(int(reg[0]["runs"]))
            if len(reg) >= 2:
                second_scores.append(int(reg[1]["runs"]))
                all_regulation_totals.append(int(reg[1]["runs"]))

        if match.get("counts_for_win_percentage") and match.get("match_winner"):
            reg = _regulation_innings(match)
            if len(reg) >= 2:
                win_eligible += 1
                first_team = reg[0]["team"]
                second_team = reg[1]["team"]
                winner = match["match_winner"]
                if winner == first_team:
                    bat_first_wins += 1
                elif winner == second_team:
                    chase_wins += 1

        perf_rows = store.performances_by_match.get(match["match_id"]) or []
        for row in perf_rows:
            wickets = row.get("wickets")
            if not wickets:
                continue
            cat = store.bowling_style_category(row.get("person_id"))
            if cat == "pace":
                pace_wkts += int(wickets)
            elif cat == "spin":
                spin_wkts += int(wickets)
            else:
                unknown_wkts += int(wickets)

    avg_first = mean(first_scores) if first_scores else None
    avg_second = mean(second_scores) if second_scores else None
    high_total = max(all_regulation_totals) if all_regulation_totals else None
    low_total = min(all_regulation_totals) if all_regulation_totals else None

    bat_first_pct = (100.0 * bat_first_wins / win_eligible) if win_eligible else None
    chase_pct = (100.0 * chase_wins / win_eligible) if win_eligible else None

    context = DataContextMeta(
        as_of_date=cutoff.as_of_date.isoformat(),
        rules_version=str(store.manifest.get("rules_version") or "1.0.0"),
        sample_size=len(historical),
    )

    notes = list(RULES_NOTES)
    if unknown_wkts and not pace_wkts and not spin_wkts:
        notes.append(
            "Pace/spin wicket split requires curated bowling_style in data/metadata/players_ipl.json."
        )

    return VenueStatsResponse(
        venue_id=venue_id,
        venue_name=venue["venue_name"],
        location=venue.get("location"),
        context=context,
        total_matches_analysed=len(historical),
        average_first_innings_score=_metric(avg_first, len(first_scores), "Average 1st innings"),
        average_second_innings_score=_metric(avg_second, len(second_scores), "Average 2nd innings"),
        highest_innings_total=_metric(high_total, len(all_regulation_totals), "Highest innings"),
        lowest_innings_total=_metric(low_total, len(all_regulation_totals), "Lowest innings"),
        batting_first_wins=_metric(bat_first_wins, win_eligible, "Batting first wins"),
        chasing_wins=_metric(chase_wins, win_eligible, "Chasing wins"),
        batting_first_win_percentage=_metric(bat_first_pct, win_eligible, "Bat first win %"),
        chasing_win_percentage=_metric(chase_pct, win_eligible, "Chase win %"),
        pace_wickets=_metric(pace_wkts, pace_wkts + spin_wkts + unknown_wkts or 0),
        spin_wickets=_metric(spin_wkts, pace_wkts + spin_wkts + unknown_wkts or 0),
        unknown_style_wickets=_metric(unknown_wkts, pace_wkts + spin_wkts + unknown_wkts or 0),
        notes=notes,
    )
