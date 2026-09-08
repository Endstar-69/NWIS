from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.risk import (
    RiskPredictionRequest, RiskPredictionResponse, ModelMetricsResponse, ShapExplanationResponse
)
from backend.app.services.risk_service import (
    predict_well_risk, get_model_evaluation_metrics, get_shap_risk_explanations
)
from backend.app.models.user import User
from backend.app.api.auth import get_current_active_user, require_engineer

router = APIRouter(prefix="/risk", tags=["ML Risk Analytics"], dependencies=[Depends(get_current_active_user)])

@router.post("/predict", response_model=RiskPredictionResponse)
def predict_risk_endpoint(
    req: RiskPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_engineer)
):
    return predict_well_risk(db, req)

@router.post("/explain", response_model=ShapExplanationResponse)
def explain_risk_endpoint(
    req: RiskPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_engineer)
):
    return get_shap_risk_explanations(db, req)

@router.get("/metrics", response_model=Dict[str, ModelMetricsResponse])
def get_metrics_endpoint():
    return get_model_evaluation_metrics()
