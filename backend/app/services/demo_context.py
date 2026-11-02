import json
from dataclasses import dataclass
from pathlib import Path

from app.utils.cutoff import CutoffContext


@dataclass(frozen=True)
class DemoConfig:
    featured_match_id: str
    historical_cutoff_date: str
    exclude_from_history_match_ids: list[str]
    matches: list[dict]

    @classmethod
    def load(cls, path: Path) -> "DemoConfig":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            featured_match_id=data["featured_match_id"],
            historical_cutoff_date=data["historical_cutoff_date"],
            exclude_from_history_match_ids=list(data.get("exclude_from_history_match_ids") or []),
            matches=list(data.get("matches") or []),
        )

    def cutoff(self) -> CutoffContext:
        return CutoffContext.from_demo_config(
            self.historical_cutoff_date,
            self.exclude_from_history_match_ids,
        )

    def get_match(self, match_id: str) -> dict | None:
        for m in self.matches:
            if m["match_id"] == match_id:
                return m
        return None
