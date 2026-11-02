import json
from pathlib import Path


def load_venue_alias_map(metadata_path: Path) -> dict[str, str]:
    """Map raw Cricsheet venue string -> canonical venue_id."""
    data = json.loads(metadata_path.read_text(encoding="utf-8"))
    alias_map: dict[str, str] = {}
    for venue in data.get("venues", []):
        venue_id = venue["venue_id"]
        for alias in venue.get("aliases", []):
            alias_map[alias.strip()] = venue_id
        alias_map[venue["venue_name"].strip()] = venue_id
    return alias_map


def normalize_venue(raw_venue: str | None, alias_map: dict[str, str]) -> str | None:
    if not raw_venue:
        return None
    cleaned = raw_venue.strip()
    return alias_map.get(cleaned)
