from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import data_store
from app.models.schemas import VenueStatsResponse
from app.services.data_loader import ProcessedDataStore
from app.services.stats.venue import compute_venue_stats

router = APIRouter(prefix="/api/venues", tags=["venues"])


@router.get("/{venue_id}/stats", response_model=VenueStatsResponse)
def venue_stats(
    venue_id: str,
    match_id: str = Query(..., description="Demo match context for historical cutoff"),
    store: ProcessedDataStore = Depends(data_store),
) -> VenueStatsResponse:
    if store.demo.get_match(match_id) is None:
        raise HTTPException(status_code=404, detail="Unknown match context")
    try:
        return compute_venue_stats(store, venue_id, store.demo.cutoff())
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
