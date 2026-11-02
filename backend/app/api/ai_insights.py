from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import data_store
from app.config import Settings, get_settings
from app.models.schemas import AIInsightsRequest, AIInsightsResponse
from app.services.ai.insights import generate_ai_insights
from app.services.data_loader import ProcessedDataStore

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/insights", response_model=AIInsightsResponse)
def ai_insights(
    body: AIInsightsRequest,
    store: ProcessedDataStore = Depends(data_store),
    settings: Settings = Depends(get_settings),
) -> AIInsightsResponse:
    try:
        return generate_ai_insights(store, settings, body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
