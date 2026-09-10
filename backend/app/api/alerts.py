from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.alert import AlertSchema, AlertAcknowledgeRequest
from backend.app.services.alert_service import get_all_alerts, acknowledge_alert
from backend.app.models.user import User
from backend.app.api.auth import get_current_active_user, require_supervisor

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertSchema])
def list_alerts_endpoint(
    well_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    return get_all_alerts(db, well_id=well_id, status=status, limit=limit)

@router.post("/{alert_id}/acknowledge", response_model=AlertSchema)
def acknowledge_alert_endpoint(
    alert_id: str,
    ack_data: AlertAcknowledgeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    updated = acknowledge_alert(db, alert_id, ack_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Alert not found")
    return updated
