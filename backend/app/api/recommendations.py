from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.alert import RecommendationSchema, GenerateRecommendationRequest
from backend.app.services.recommendation_service import (
    get_recommendations_for_well, generate_dynamic_recommendation
)
from backend.app.api.auth import get_current_active_user

router = APIRouter(prefix="/recommendations", tags=["Recommendations"], dependencies=[Depends(get_current_active_user)])

@router.get("/{well_id}", response_model=List[RecommendationSchema])
def get_well_recommendations(
    well_id: str,
    depth: Optional[float] = Query(None, description="Optional target depth override"),
    hazard: Optional[str] = Query(None, description="Optional dominant hazard override (MUD_LOSS, STUCK_PIPE, KICK)"),
    force_refresh: bool = Query(False, description="Force dynamic recalculation bypassing cache"),
    db: Session = Depends(get_db)
):
    return get_recommendations_for_well(db, well_id, depth=depth, hazard=hazard, force_refresh=force_refresh)

@router.post("/generate", response_model=RecommendationSchema)
def generate_recommendation_endpoint(
    req: GenerateRecommendationRequest,
    db: Session = Depends(get_db)
):
    return generate_dynamic_recommendation(
        db=db,
        well_id=req.well_id,
        depth=req.depth,
        formation=req.formation,
        active_hazard=req.active_hazard
    )
