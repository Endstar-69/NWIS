import json
from typing import Dict, List, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.models.event import DrillingEvent
from backend.app.models.well import Well
from backend.app.schemas.risk import (
    RiskPredictionRequest, RiskPredictionResponse, ModelMetricsResponse, ShapExplanationResponse
)
from backend.app.ml.inference import inference_engine
from backend.app.services.alert_service import create_proactive_alert_if_needed

def predict_well_risk(db: Session, req: RiskPredictionRequest) -> RiskPredictionResponse:
    # 1. Fetch nearby offset well historical events in depth window
    offset_events = db.query(DrillingEvent).filter(
        DrillingEvent.start_depth >= req.depth - 150.0,
        DrillingEvent.start_depth <= req.depth + 150.0
    ).limit(5).all()

    historical_evidence = [
        {
            "event_id": e.event_id,
            "well_id": e.well_id,
            "depth": e.start_depth,
            "event_type": e.event_type,
            "formation": e.formation,
            "severity": e.severity,
            "mitigation": e.mitigation
        }
        for e in offset_events
    ]

    # 2. Run ML Inference with Explainability
    raw_dict = req.model_dump()
    predictions = inference_engine.predict_risk(raw_dict, historical_evidence)

    # 3. Overall Risk Level determination
    max_prob = max(p.probability for p in predictions.values())
    if max_prob >= 0.75:
        overall_risk = "CRITICAL" if max_prob >= 0.85 else "HIGH"
    elif max_prob >= 0.40:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    # 4. Proactive Alert Triggering for high risk predictions
    for r_type, p_obj in predictions.items():
        if p_obj.probability >= 0.65:
            reasons_text = [f.description for f in p_obj.contributing_factors]
            action = f"Verify well control barriers and prepare contingency LCM / jarring pill across {req.formation_name}."
            create_proactive_alert_if_needed(
                db=db,
                well_id=req.well_id,
                depth=req.depth,
                formation=req.formation_name,
                risk_type=r_type,
                probability=p_obj.probability,
                reasons=reasons_text,
                historical_evidence=historical_evidence,
                recommended_action=action
            )

    return RiskPredictionResponse(
        well_id=req.well_id,
        depth=req.depth,
        formation_name=req.formation_name,
        overall_risk_level=overall_risk,
        predictions=predictions,
        nearby_historical_evidence=historical_evidence,
        model_version="RandomForest-v1.0 (Balanced)",
        is_demo_prediction=True
    )

def get_shap_risk_explanations(db: Session, req: RiskPredictionRequest) -> ShapExplanationResponse:
    """Computes exact Tree SHAP feature attributions alongside physics warnings."""
    offset_events = db.query(DrillingEvent).filter(
        DrillingEvent.start_depth >= req.depth - 150.0,
        DrillingEvent.start_depth <= req.depth + 150.0
    ).limit(5).all()

    historical_evidence = [
        {
            "event_id": e.event_id,
            "well_id": e.well_id,
            "depth": e.start_depth,
            "event_type": e.event_type,
            "formation": e.formation,
            "severity": e.severity,
            "mitigation": e.mitigation
        }
        for e in offset_events
    ]

    raw_dict = req.model_dump()
    predictions = inference_engine.predict_risk(raw_dict, historical_evidence)

    shap_map = {r_type: p.shap_attribution for r_type, p in predictions.items()}
    warnings_map = {r_type: p.engineering_warnings for r_type, p in predictions.items()}

    return ShapExplanationResponse(
        well_id=req.well_id,
        depth=req.depth,
        formation_name=req.formation_name,
        shap_explanations=shap_map,
        engineering_warnings=warnings_map,
        classification="[D] Optional Advanced Enterprise Integration / Supervised ML Benchmark",
        methodology="TreeExplainer (Tree SHAP exact feature attribution) strictly separated from deterministic physics warnings"
    )

def get_model_evaluation_metrics() -> Dict[str, ModelMetricsResponse]:
    eval_file = Path(settings.EVAL_DIR) / "model_metrics.json"
    if not eval_file.exists():
        return {}

    with open(eval_file, "r") as f:
        data = json.load(f)

    result = {}
    for k, v in data.items():
        result[k] = ModelMetricsResponse(**v)
    return result
