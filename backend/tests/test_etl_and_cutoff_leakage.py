import json
from pathlib import Path

from app.services.cricsheet_etl import parse_match_file
from app.utils.cutoff import CutoffContext
from app.utils.venues import load_venue_alias_map

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
METADATA_VENUES = ROOT / "data" / "metadata" / "venues.json"
DEMO = json.loads((ROOT / "data" / "metadata" / "demo_matches.json").read_text(encoding="utf-8"))


def test_demo_match_parses_wankhede_and_super_over_flags() -> None:
    path = RAW / "1426267.json"
    if not path.exists():
        return
    alias_map = load_venue_alias_map(METADATA_VENUES)
    row = parse_match_file(path, alias_map)
    assert row["venue_id"] == "wankhede_mumbai"
    assert row["match_date"] == "2024-04-14"
    assert all(not inn["is_super_over"] for inn in row["innings"])


def test_cutoff_leakage_demo_match_not_in_history() -> None:
    ctx = CutoffContext.from_demo_config(
        DEMO["historical_cutoff_date"],
        DEMO["exclude_from_history_match_ids"],
    )
    assert not ctx.includes_match("1426267", "2024-04-14")


def test_processed_build_match_count_when_raw_present() -> None:
    manifest_path = ROOT / "data" / "processed" / "manifest.json"
    if not manifest_path.exists():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw_count = len(list(RAW.glob("*.json")))
    assert manifest["raw_match_count"] == raw_count


def test_performance_null_when_player_only_fields() -> None:
    path = RAW / "1426267.json"
    if not path.exists():
        return
    alias_map = load_venue_alias_map(METADATA_VENUES)
    row = parse_match_file(path, alias_map)
    perf = row["performances"]
    bumrah = next(p for p in perf if p["player_name"] == "JJ Bumrah")
    assert bumrah["runs"] is None
    assert bumrah["balls_faced"] is None
    assert bumrah["runs_conceded"] is not None
