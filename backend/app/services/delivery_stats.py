"""Ball-by-ball counting rules — see backend/docs/STATS_RULES.md."""

from dataclasses import dataclass, field

BOWLER_NON_CREDIT_KINDS = frozenset({"run out", "retired out", "retired hurt"})


def is_wide(delivery: dict) -> bool:
    extras = delivery.get("extras") or {}
    return "wides" in extras


def is_noball(delivery: dict) -> bool:
    extras = delivery.get("extras") or {}
    return "noballs" in extras


def is_legal_ball(delivery: dict) -> bool:
    return not is_wide(delivery) and not is_noball(delivery)


def bowler_credited_wickets(delivery: dict) -> int:
    if "wickets" not in delivery:
        return 0
    count = 0
    for wicket in delivery["wickets"]:
        kind = (wicket.get("kind") or "").lower()
        if kind in BOWLER_NON_CREDIT_KINDS:
            continue
        count += 1
    return count


def innings_wicket_count(delivery: dict) -> int:
    return len(delivery.get("wickets") or [])


@dataclass
class PlayerInningsAccumulator:
    runs: int = 0
    balls_faced: int = 0
    runs_conceded: int = 0
    legal_balls_bowled: int = 0
    wickets: int = 0
    batted: bool = False
    bowled: bool = False


@dataclass
class MatchDeliveryStats:
    players: dict[str, PlayerInningsAccumulator] = field(default_factory=dict)

    def _acc(self, name: str) -> PlayerInningsAccumulator:
        if name not in self.players:
            self.players[name] = PlayerInningsAccumulator()
        return self.players[name]

    def process_delivery(self, delivery: dict) -> None:
        batter = delivery["batter"]
        bowler = delivery["bowler"]
        runs = delivery.get("runs") or {}
        batter_runs = int(runs.get("batter") or 0)
        total_runs = int(runs.get("total") or 0)
        legal = is_legal_ball(delivery)

        b_acc = self._acc(batter)
        b_acc.batted = True
        b_acc.runs += batter_runs
        if legal:
            b_acc.balls_faced += 1

        bw_acc = self._acc(bowler)
        bw_acc.bowled = True
        bw_acc.runs_conceded += total_runs
        if legal:
            bw_acc.legal_balls_bowled += 1
        bw_acc.wickets += bowler_credited_wickets(delivery)


def innings_total_runs(deliveries: list[dict]) -> int:
    return sum(int((d.get("runs") or {}).get("total") or 0) for d in deliveries)


def innings_total_wickets(deliveries: list[dict]) -> int:
    return sum(innings_wicket_count(d) for d in deliveries)


def collect_innings_deliveries(innings: dict) -> list[dict]:
    out: list[dict] = []
    for over in innings.get("overs") or []:
        out.extend(over.get("deliveries") or [])
    return out
