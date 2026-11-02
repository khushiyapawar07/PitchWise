from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CutoffContext:
    """Pre-match historical boundary for the featured demo."""

    as_of_date: date
    exclude_match_ids: frozenset[str]

    @classmethod
    def from_demo_config(cls, cutoff_iso: str, exclude_ids: list[str]) -> "CutoffContext":
        return cls(
            as_of_date=date.fromisoformat(cutoff_iso),
            exclude_match_ids=frozenset(exclude_ids),
        )

    def includes_match(self, match_id: str, match_date_iso: str) -> bool:
        if match_id in self.exclude_match_ids:
            return False
        return date.fromisoformat(match_date_iso) <= self.as_of_date
