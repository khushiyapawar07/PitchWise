"""Classify match outcomes for venue aggregates — see STATS_RULES.md."""

from typing import Literal

ResultType = Literal["normal", "tie", "no_result"]


def classify_result(info: dict) -> ResultType:
    outcome = info.get("outcome") or {}
    result = (outcome.get("result") or "").lower()
    if result == "no result":
        return "no_result"
    if result == "tie":
        return "tie"
    return "normal"


def counts_for_win_percentage(result_type: ResultType) -> bool:
    return result_type == "normal"


def counts_for_venue_regulation_innings_averages(result_type: ResultType) -> bool:
    return result_type in {"normal", "tie"}


def match_winner(info: dict) -> str | None:
    outcome = info.get("outcome") or {}
    return outcome.get("winner") or outcome.get("eliminator")
