from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import data_store
from app.models.schemas import ComparePlayersRequest, ComparePlayersResponse
from app.services.data_loader import ProcessedDataStore
from app.services.stats.compare import compare_players

router = APIRouter(prefix="/api", tags=["compare"])


@router.post("/compare", response_model=ComparePlayersResponse)
def compare(
    body: ComparePlayersRequest,
    store: ProcessedDataStore = Depends(data_store),
) -> ComparePlayersResponse:
    try:
        return compare_players(store, body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
