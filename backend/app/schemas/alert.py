from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class AlertSchema(BaseModel):
    alert_id: str
    well_id: str
    timestamp: datetime
    depth: float
    formation: str
    risk_type: str
    severity: str # INFO, WATCH, HIGH, CRITICAL
    probability: float
    reasons: List[str]
    historical_evidence: List[dict]
    recommended_action: str
    status: str # NEW, ACKNOWLEDGED, RESOLVED
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    is_demo_data: bool = True

    class Config:
        from_attributes = True

class AlertAcknowledgeRequest(BaseModel):
    acknowledged_by: str
    notes: Optional[str] = None

class GenerateRecommendationRequest(BaseModel):
    well_id: str
    depth: Optional[float] = None
    formation: Optional[str] = None
    active_hazard: Optional[str] = None

class RecommendationSchema(BaseModel):
    recommendation_id: str
    well_id: str
    depth: float
    formation: str
    title: str
    summary: str
    dominant_hazard: Optional[str] = None
    hazard_level: Optional[str] = None
    historical_evidence: List[dict]
    evidence_sources: List[dict] = []
    action_steps: List[str]
    precautions: List[str]
    confidence: float
    provenance: Optional[dict] = None
    created_at: Optional[datetime] = None
    is_demo_data: bool = True

    class Config:
        from_attributes = True
