from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class RiskFactorDetail(BaseModel):
    factor_name: str
    impact_level: str  # HIGH, MEDIUM, LOW
    description: str
    # Engineering threshold weight — derived from physics rules (Teale MSE, ECD, hydraulic balance)
    contribution_score: float  # 0.0 - 1.0

class FeatureShapAttribution(BaseModel):
    feature_name: str
    feature_value: float
    shap_value: float  # Directional additive contribution (positive increases risk, negative decreases)
    absolute_importance: float  # abs(shap_value)
    impact_direction: str  # INCREASES_RISK | DECREASES_RISK | NEUTRAL

class ModelShapExplanation(BaseModel):
    base_value: float  # Expected model output E[f(x)]
    prediction_value: float  # Model output f(x)
    top_features: List[FeatureShapAttribution]
    methodology: str = "TreeExplainer (Tree SHAP exact feature attribution)"
    provenance: str = "[D] Supervised ML Benchmark TreeExplainer"

class SingleRiskPrediction(BaseModel):
    risk_type: str  # MUD_LOSS, STUCK_PIPE, KICK
    probability: float  # 0.0 - 1.0
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence_score: float
    contributing_factors: List[RiskFactorDetail]  # Retained for backwards compatibility
    engineering_warnings: List[RiskFactorDetail] = []  # Explicit physics-grounded engineering warnings
    shap_attribution: Optional[ModelShapExplanation] = None  # Genuine Tree SHAP feature attributions
    shap_summary: Optional[Dict[str, float]] = None  # Feature to SHAP value mapping
    historical_matches_count: int
    offset_incident_rate: float
    # Which risk computation tier produced this prediction:
    # "hybrid_physics_statistical" = Tier 1 Physics + Tier 2 Rolling Z-Score / Isolation Forest
    # "hybrid_physics_statistical_ml" = Tier 1 Physics + Tier 2 Statistics + Tier 3 ML
    # "tier1_physics" = deterministic engineering physics only
    # "supervised_ml_benchmark" = optional ML model validation
    risk_engine_tier: str = "hybrid_physics_statistical"
    tier1_physics_score: Optional[float] = None
    tier2_statistical_score: Optional[float] = None
    z_score_anomalies: Optional[Dict[str, float]] = None
    isolation_forest_outlier: Optional[bool] = None
    supervised_ml_score: Optional[float] = None
    provenance: Optional[Dict[str, Any]] = None

class RiskPredictionRequest(BaseModel):
    well_id: str
    depth: float
    formation_name: str
    rop: float  # m/hr
    wob: float  # tons
    rpm: float  # RPM
    torque: float  # kNm
    standpipe_pressure: float  # psi
    flow_rate: float  # LPM
    mud_weight: float  # SG
    ecd: float  # SG
    hook_load: float  # tons
    inclination: Optional[float] = 0.0
    azimuth: Optional[float] = 0.0
    flow_in: Optional[float] = None
    flow_out: Optional[float] = None
    delta_flow: Optional[float] = None
    pit_volume: Optional[float] = None
    gas_units: Optional[float] = None

class RiskPredictionResponse(BaseModel):
    well_id: str
    depth: float
    formation_name: str
    overall_risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    predictions: Dict[str, SingleRiskPrediction]
    nearby_historical_evidence: List[dict]
    proactive_recommendation: Optional[dict] = None
    model_version: str = "tier1_physics_heuristics_v1.0"
    # True when this prediction uses synthetic/demo data or heuristic-only engine
    is_demo_prediction: bool = True

class ModelMetricsResponse(BaseModel):
    model_name: str
    target_event: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: Optional[float] = None
    confusion_matrix: List[List[int]]
    feature_importances: Dict[str, float]
    training_sample_count: int
    trained_at: str
    classification: Optional[str] = "[D] Optional Advanced Enterprise Integration / Benchmark"
    evaluation_methodology: Optional[str] = "5-Fold GroupKFold Cross-Validation by well_id (Zero Target Leakage)"
    disclaimer: Optional[str] = None

class ShapExplanationResponse(BaseModel):
    well_id: str
    depth: float
    formation_name: str
    shap_explanations: Dict[str, Optional[ModelShapExplanation]]
    engineering_warnings: Dict[str, List[RiskFactorDetail]]
    classification: str = "[D] Optional Advanced Enterprise Integration / Supervised ML Benchmark"
    methodology: str = "TreeExplainer (Tree SHAP exact feature attribution) strictly separated from deterministic physics warnings"
