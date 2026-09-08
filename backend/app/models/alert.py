from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from datetime import datetime, timezone
from backend.app.core.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(String(50), primary_key=True, index=True)
    well_id = Column(String(50), ForeignKey("wells.well_id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    depth = Column(Float, nullable=False)
    formation = Column(String(100), nullable=False)
    risk_type = Column(String(50), nullable=False) # MUD_LOSS, STUCK_PIPE, KICK, OVERPRESSURE
    severity = Column(String(20), nullable=False, default="HIGH") # INFO, WATCH, HIGH, CRITICAL
    probability = Column(Float, nullable=False, default=0.75) # 0.0 - 1.0
    reasons_json = Column(Text, nullable=False) # List of contributing factors
    historical_evidence_json = Column(Text, nullable=False) # List of matching offset well incidents
    recommended_action = Column(Text, nullable=False)
    status = Column(String(20), default="NEW", index=True) # NEW, ACKNOWLEDGED, RESOLVED
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    is_demo_data = Column(Boolean, default=True)


class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(String(50), primary_key=True, index=True)
    well_id = Column(String(50), ForeignKey("wells.well_id"), nullable=False, index=True)
    depth = Column(Float, nullable=False)
    formation = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)
    historical_evidence_json = Column(Text, nullable=False)
    action_steps_json = Column(Text, nullable=False)
    precautions_json = Column(Text, nullable=False)
    confidence = Column(Float, default=0.88)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_demo_data = Column(Boolean, default=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    username = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False) # LOGIN, SEARCH, ACKNOWLEDGE_ALERT, UPLOAD_DOCUMENT, PREDICT_RISK
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details_json = Column(Text, nullable=True)
