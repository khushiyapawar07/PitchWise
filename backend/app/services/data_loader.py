import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.config import Settings, get_settings
from app.services.demo_context import DemoConfig
from app.utils.venues import load_venue_alias_map


class ProcessedDataStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.manifest: dict[str, Any] = json.loads(
            (settings.data_processed_dir / "manifest.json").read_text(encoding="utf-8")
        )
        self.matches: list[dict[str, Any]] = json.loads(
            (settings.data_processed_dir / "matches.json").read_text(encoding="utf-8")
        )
        self.performances_by_match: dict[str, list[dict[str, Any]]] = json.loads(
            (settings.data_processed_dir / "performances_by_match.json").read_text(encoding="utf-8")
        )
        self.demo = DemoConfig.load(settings.data_metadata_dir / "demo_matches.json")
        self.venue_catalog = json.loads(
            (settings.data_metadata_dir / "venues.json").read_text(encoding="utf-8")
        )
        self._venue_by_id = {v["venue_id"]: v for v in self.venue_catalog.get("venues", [])}
        self.players_meta = json.loads(
            (settings.data_metadata_dir / "players_ipl.json").read_text(encoding="utf-8")
        ).get("players") or {}
        self._matches_by_id = {m["match_id"]: m for m in self.matches}

    def venue_record(self, venue_id: str) -> dict | None:
        return self._venue_by_id.get(venue_id)

    def match_by_id(self, match_id: str) -> dict | None:
        return self._matches_by_id.get(match_id)

    def player_metadata(self, person_id: str | None) -> dict[str, str]:
        if not person_id:
            return {
                "playing_role": "unknown",
                "batting_style": "unknown",
                "bowling_style": "unknown",
            }
        row = self.players_meta.get(person_id) or {}
        return {
            "playing_role": row.get("playing_role") or "unknown",
            "batting_style": row.get("batting_style") or "unknown",
            "bowling_style": row.get("bowling_style") or "unknown",
        }

    def bowling_style_category(self, person_id: str | None) -> str:
        style = self.player_metadata(person_id)["bowling_style"].lower()
        if style == "pace":
            return "pace"
        if style == "spin":
            return "spin"
        return "unknown"


@lru_cache
def get_data_store() -> ProcessedDataStore:
    return ProcessedDataStore(get_settings())


def reset_data_store_cache() -> None:
    get_data_store.cache_clear()
