from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import data_store
from app.models.schemas import PlayerListItem, PlayerStatsResponse
from app.services.data_loader import ProcessedDataStore
from app.services.stats.player import compute_player_stats, list_players_for_match

router = APIRouter(prefix="/api/players", tags=["players"])


@router.get("", response_model=list[PlayerListItem])
def list_players(
    match_id: str = Query(...),
    store: ProcessedDataStore = Depends(data_store),
) -> list[PlayerListItem]:
    try:
        return list_players_for_match(store, match_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{player_id}/stats", response_model=PlayerStatsResponse)
def player_stats(
    player_id: str,
    match_id: str = Query(...),
    store: ProcessedDataStore = Depends(data_store),
) -> PlayerStatsResponse:
    try:
        return compute_player_stats(store, match_id, player_id, store.demo.cutoff())
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
