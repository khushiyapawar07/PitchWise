"""Build JSON processed dataset from Cricsheet raw files (does not modify raw)."""

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import get_settings  # noqa: E402
from app.services.cricsheet_etl import build_processed_dataset  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Build PitchWise processed JSON from Cricsheet raw data")
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=None,
        help="Override path to data/raw",
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=None,
        help="Override path to data/processed",
    )
    args = parser.parse_args()
    settings = get_settings()
    raw_dir = (args.raw_dir or settings.data_raw_dir).resolve()
    processed_dir = (args.processed_dir or settings.data_processed_dir).resolve()
    metadata_venues = (settings.data_metadata_dir / "venues.json").resolve()

    if not raw_dir.is_dir():
        raise SystemExit(f"Raw data directory not found: {raw_dir}")

    manifest = build_processed_dataset(raw_dir, metadata_venues, processed_dir)
    print(
        f"Built {manifest['raw_match_count']} matches -> {processed_dir} "
        f"(rules {manifest['rules_version']})"
    )
    if manifest.get("unknown_venue_strings"):
        print(f"Warning: {len(manifest['unknown_venue_strings'])} unmapped venue strings (see manifest.json)")


if __name__ == "__main__":
    main()
