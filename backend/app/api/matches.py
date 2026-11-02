from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import data_store
from app.models.schemas import DemoMatchSummary, MatchDetail
from app.services.data_loader import ProcessedDataStore

router = APIRouter(prefix="/api/matches", tags=["matches"])


def _demo_match_summary(store: ProcessedDataStore, demo: dict) -> DemoMatchSummary:
    venue = store.venue_record(demo["venue_id"])
    if venue is None:
        raise HTTPException(status_code=500, detail="Demo venue metadata missing")
    return DemoMatchSummary(
        match_id=demo["match_id"],
        display_title=demo["display_title"],
        team_1=demo["team_1"],
        team_2=demo["team_2"],
        venue_id=demo["venue_id"],
        venue_name=venue["venue_name"],
        match_date=demo["match_date"],
        match_format=demo["match_format"],
    )


@router.get("", response_model=list[DemoMatchSummary])
def list_demo_matches(store: ProcessedDataStore = Depends(data_store)) -> list[DemoMatchSummary]:
    return [_demo_match_summary(store, m) for m in store.demo.matches]


@router.get("/{match_id}", response_model=MatchDetail)
def get_match(match_id: str, store: ProcessedDataStore = Depends(data_store)) -> MatchDetail:
    demo = store.demo.get_match(match_id)
    if demo is None:
        raise HTTPException(status_code=404, detail="Match not found")

    summary = _demo_match_summary(store, demo)
    processed = store.match_by_id(match_id)
    return MatchDetail(
        **summary.model_dump(),
        city=(processed or {}).get("city"),
        toss_winner=(processed or {}).get("toss_winner"),
        toss_decision=(processed or {}).get("toss_decision"),
        historical_cutoff_date=store.demo.historical_cutoff_date,
        excluded_from_history=True,
    )
