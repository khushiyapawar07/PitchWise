from app.services.data_loader import ProcessedDataStore, reset_data_store_cache
from app.services.demo_context import DemoConfig
from app.services.stats.venue import compute_venue_stats
from app.config import get_settings


def test_missing_values_not_zero_averages() -> None:
    reset_data_store_cache()
    store = ProcessedDataStore(get_settings())
    demo = DemoConfig.load(get_settings().data_metadata_dir / "demo_matches.json")
    stats = compute_venue_stats(store, "wankhede_mumbai", demo.cutoff())
    if stats.average_first_innings_score.sample_size == 0:
        assert stats.average_first_innings_score.value is None
    else:
        assert stats.average_first_innings_score.value is not None
