import json
from pathlib import Path

from app.services.delivery_stats import (
    MatchDeliveryStats,
    bowler_credited_wickets,
    is_legal_ball,
    is_noball,
    is_wide,
)

FIXTURES = Path(__file__).parent / "fixtures" / "delivery_samples.json"


def _samples() -> dict:
    return json.loads(FIXTURES.read_text(encoding="utf-8"))


def test_wide_is_not_legal_ball() -> None:
    wide = _samples()["wide_then_legal"][0]
    assert is_wide(wide)
    assert not is_legal_ball(wide)


def test_noball_is_not_legal_ball() -> None:
    nb = _samples()["noball_with_bat_runs"][0]
    assert is_noball(nb)
    assert not is_legal_ball(nb)


def test_batter_runs_and_balls_faced_wide_then_four() -> None:
    stats = MatchDeliveryStats()
    for d in _samples()["wide_then_legal"]:
        stats.process_delivery(d)
    a = stats.players["A"]
    assert a.runs == 4
    assert a.balls_faced == 1
    b = stats.players["B"]
    assert b.runs_conceded == 5
    assert b.legal_balls_bowled == 1


def test_noball_batter_runs_no_ball_faced() -> None:
    stats = MatchDeliveryStats()
    stats.process_delivery(_samples()["noball_with_bat_runs"][0])
    a = stats.players["A"]
    assert a.runs == 1
    assert a.balls_faced == 0
    b = stats.players["B"]
    assert b.runs_conceded == 2


def test_run_out_not_bowler_wicket() -> None:
    d = _samples()["run_out"][0]
    assert bowler_credited_wickets(d) == 0
    stats = MatchDeliveryStats()
    stats.process_delivery(d)
    assert stats.players["B"].wickets == 0


def test_caught_is_bowler_wicket() -> None:
    d = _samples()["bowler_wicket"][0]
    assert bowler_credited_wickets(d) == 1
