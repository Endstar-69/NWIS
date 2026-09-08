import json
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.models.alert import Alert
from backend.app.models.well import Well
from backend.app.schemas.alert import AlertSchema, AlertAcknowledgeRequest

def get_all_alerts(db: Session, well_id: Optional[str] = None, status: Optional[str] = None, limit: int = 50) -> List[AlertSchema]:
    query = db.query(Alert)
    if well_id:
        query = query.filter(Alert.well_id == well_id)
    if status:
        query = query.filter(Alert.status == status)
    
    alerts = query.order_by(Alert.timestamp.desc()).limit(limit).all()
    
    res = []
    for a in alerts:
        try:
            reasons = json.loads(a.reasons_json) if a.reasons_json else []
        except Exception:
            reasons = [a.reasons_json]

        try:
            evidence = json.loads(a.historical_evidence_json) if a.historical_evidence_json else []
        except Exception:
            evidence = []

        res.append(AlertSchema(
            alert_id=a.alert_id,
            well_id=a.well_id,
            timestamp=a.timestamp,
            depth=a.depth,
            formation=a.formation,
            risk_type=a.risk_type,
            severity=a.severity,
            probability=a.probability,
            reasons=reasons,
            historical_evidence=evidence,
            recommended_action=a.recommended_action,
            status=a.status,
            acknowledged_by=a.acknowledged_by,
            acknowledged_at=a.acknowledged_at,
            is_demo_data=a.is_demo_data
        ))
    return res

def acknowledge_alert(db: Session, alert_id: str, ack_data: AlertAcknowledgeRequest) -> Optional[AlertSchema]:
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        return None

    alert.status = "ACKNOWLEDGED"
    alert.acknowledged_by = ack_data.acknowledged_by
    alert.acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)

    try:
        reasons = json.loads(alert.reasons_json) if alert.reasons_json else []
    except Exception:
        reasons = [alert.reasons_json]

    try:
        evidence = json.loads(alert.historical_evidence_json) if alert.historical_evidence_json else []
    except Exception:
        evidence = []

    return AlertSchema(
        alert_id=alert.alert_id,
        well_id=alert.well_id,
        timestamp=alert.timestamp,
        depth=alert.depth,
        formation=alert.formation,
        risk_type=alert.risk_type,
        severity=alert.severity,
        probability=alert.probability,
        reasons=reasons,
        historical_evidence=evidence,
        recommended_action=alert.recommended_action,
        status=alert.status,
        acknowledged_by=alert.acknowledged_by,
        acknowledged_at=alert.acknowledged_at,
        is_demo_data=alert.is_demo_data
    )

def create_proactive_alert_if_needed(
    db: Session,
    well_id: str,
    depth: float,
    formation: str,
    risk_type: str,
    probability: float,
    reasons: List[str],
    historical_evidence: List[dict],
    recommended_action: str
) -> Optional[Alert]:
    # Check severity threshold
    if probability < 0.40:
        return None

    severity = "CRITICAL" if probability >= 0.85 else ("HIGH" if probability >= 0.70 else "WATCH")

    # Prevent duplicate alert within 20m window
    recent_similar = db.query(Alert).filter(
        Alert.well_id == well_id,
        Alert.risk_type == risk_type,
        Alert.depth >= depth - 15.0,
        Alert.depth <= depth + 15.0
    ).first()

    if recent_similar:
        return None

    new_alert = Alert(
        alert_id=f"ALT-{int(datetime.now().timestamp() * 1000) % 1000000:06d}",
        well_id=well_id,
        timestamp=datetime.now(timezone.utc),
        depth=round(depth, 1),
        formation=formation,
        risk_type=risk_type,
        severity=severity,
        probability=round(probability, 2),
        reasons_json=json.dumps(reasons),
        historical_evidence_json=json.dumps(historical_evidence),
        recommended_action=recommended_action,
        status="NEW",
        is_demo_data=True
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert
