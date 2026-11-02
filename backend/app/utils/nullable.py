from typing import TypeVar

T = TypeVar("T")


def unavailable() -> None:
    return None


def coalesce_count(value: int | None) -> int | None:
    """Return None when the player had no activity in that category (not zero runs)."""
    if value is None:
        return None
    return value
