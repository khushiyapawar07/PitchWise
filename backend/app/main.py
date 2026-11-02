from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ai_insights, compare, matches, players, venues
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="PitchWise API",
    description="Cricket decision intelligence — historical stats and AI insights",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(matches.router)
app.include_router(venues.router)
app.include_router(players.router)
app.include_router(compare.router)
app.include_router(ai_insights.router)


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "ai_configured": bool(settings.gemini_api_key.strip()),
    }
