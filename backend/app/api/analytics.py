from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.services.analytics_service import analytics_service
from backend.app.api.auth import get_current_active_user

router = APIRouter(prefix="/analytics", tags=["Advanced Analytics & Innovation"], dependencies=[Depends(get_current_active_user)])

@router.get("/knowledge-graph")
def get_knowledge_graph(db: Session = Depends(get_db)):
    """Returns graph topology linking Wells, Formations, Events, Causes, and Mitigations."""
    return analytics_service.get_knowledge_graph(db)

@router.get("/risk-heatmap")
def get_risk_heatmap(db: Session = Depends(get_db)):
    """Returns 2D depth intervals by formation risk density heatmap."""
    return analytics_service.get_risk_heatmap(db)

@router.post("/what-if")
def simulate_what_if(payload: Dict[str, Any] = Body(...)):
    """Interactive What-If parameter simulation sandbox."""
    return analytics_service.simulate_what_if(payload)

@router.get("/npt-cost")
def get_npt_cost_intelligence(db: Session = Depends(get_db)):
    """Returns quantified NPT hours, financial loss breakdown, and projected NWIS savings."""
    return analytics_service.get_npt_and_cost_intelligence(db)

@router.get("/depth-explorer")
def get_depth_explorer(
    depth: float = Query(3420.0, description="Target prospective depth in meters"),
    db: Session = Depends(get_db)
):
    """Explores prospective drilling depth for upcoming lithology, offset incidents, and predicted risk."""
    return analytics_service.get_depth_explorer(db, depth)

@router.get("/daily-report")
def get_daily_intelligence_report(
    well_id: str = Query(None, description="Active Well ID"),
    db: Session = Depends(get_db)
):
    """Generates an exportable Daily Drilling Intelligence Report."""
    return analytics_service.generate_daily_intelligence_report(db, well_id)

@router.get("/predictive-timeline")
def get_predictive_timeline(
    depth: float = Query(3420.0, description="Current depth in meters"),
    db: Session = Depends(get_db)
):
    """Forward-looking lookahead timeline for upcoming 350m of drilling."""
    return analytics_service.get_predictive_timeline(db, depth)
