from pathlib import Path

from app.utils.venues import load_venue_alias_map, normalize_venue

METADATA = Path(__file__).resolve().parents[2] / "data" / "metadata" / "venues.json"


def test_wankhede_aliases_normalize_to_one_id() -> None:
    alias_map = load_venue_alias_map(METADATA)
    a = normalize_venue("Wankhede Stadium", alias_map)
    b = normalize_venue("Wankhede Stadium, Mumbai", alias_map)
    assert a == b == "wankhede_mumbai"
