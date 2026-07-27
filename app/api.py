from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.config import get_settings
from app.engine import TrustDIEngine


class MatchRequest(BaseModel):
    source_csv: str = Field(..., description="Path to source CSV")
    target_csv: str = Field(..., description="Path to target CSV")
    gold: dict[str, str] | None = Field(default=None, description="Optional gold mapping")


class ProfileRequest(BaseModel):
    csv_path: str
    dataset_id: str | None = None


app = FastAPI(
    title="TrustDI Agentic RAG API",
    description="Agentic RAG system for trustworthy and cost-efficient data integration.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, Any]:
    settings = get_settings()
    return {
        "status": "ok",
        "openai_enabled": settings.openai_enabled,
        "external_kb_enabled": settings.external_kb_enabled,
        "model": settings.openai_model,
    }


@app.post("/profile")
def profile(request: ProfileRequest) -> dict[str, Any]:
    engine = TrustDIEngine()
    profile_result = engine.profile_csv(Path(request.csv_path), dataset_id=request.dataset_id)
    return profile_result.to_dict()


@app.post("/match")
def match(request: MatchRequest) -> dict[str, Any]:
    engine = TrustDIEngine()
    result = engine.match_csvs(request.source_csv, request.target_csv, gold=request.gold)
    return result.to_dict()


@app.post("/evaluate")
def evaluate(request: MatchRequest) -> dict[str, Any]:
    engine = TrustDIEngine()
    result = engine.match_csvs(request.source_csv, request.target_csv, gold=request.gold)
    return {"metrics": result.metrics, "matches": [match.to_dict() for match in result.matches]}

