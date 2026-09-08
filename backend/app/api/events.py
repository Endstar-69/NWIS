from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.event import DrillingEvent
from backend.app.models.well import Well
from backend.app.models.user import User
from backend.app.schemas.event import DrillingEventSchema, DrillingEventCreate
from backend.app.api.auth import get_current_active_user, require_engineer

router = APIRouter(prefix="/events", tags=["Knowledge Repository Events"], dependencies=[Depends(get_current_active_user)])

@router.get("", response_model=List[DrillingEventSchema])
def list_events(
    well_id: Optional[str] = None,
    formation: Optional[str] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    min_depth: Optional[float] = None,
    max_depth: Optional[float] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(DrillingEvent)
    if well_id:
        query = query.filter(DrillingEvent.well_id == well_id)
    if formation:
        query = query.filter(DrillingEvent.formation.ilike(f"%{formation}%"))
    if event_type:
        query = query.filter(DrillingEvent.event_type == event_type)
    if severity:
        query = query.filter(DrillingEvent.severity == severity)
    if min_depth is not None:
        query = query.filter(DrillingEvent.start_depth >= min_depth)
    if max_depth is not None:
        query = query.filter(DrillingEvent.start_depth <= max_depth)

    events = query.order_by(DrillingEvent.start_depth.asc()).offset(offset).limit(limit).all()
    well_cache = {w.well_id: w.well_name for w in db.query(Well).all()}

    res = []
    for e in events:
        res.append(DrillingEventSchema(
            event_id=e.event_id,
            well_id=e.well_id,
            event_type=e.event_type,
            start_depth=e.start_depth,
            end_depth=e.end_depth,
            formation=e.formation,
            severity=e.severity,
            cause=e.cause,
            impact=e.impact,
            mitigation=e.mitigation,
            lesson_learned=e.lesson_learned,
            npt_hours=e.npt_hours,
            source_document=e.source_document,
            source_page=e.source_page,
            confidence=e.confidence,
            is_demo_data=e.is_demo_data,
            created_at=e.created_at,
            well_name=well_cache.get(e.well_id, e.well_id)
        ))
    return res

@router.get("/{event_id}", response_model=DrillingEventSchema)
def get_event(event_id: str, db: Session = Depends(get_db)):
    event = db.query(DrillingEvent).filter(DrillingEvent.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")
    well = db.query(Well).filter(Well.well_id == event.well_id).first()
    return DrillingEventSchema(
        event_id=event.event_id,
        well_id=event.well_id,
        event_type=event.event_type,
        start_depth=event.start_depth,
        end_depth=event.end_depth,
        formation=event.formation,
        severity=event.severity,
        cause=event.cause,
        impact=event.impact,
        mitigation=event.mitigation,
        lesson_learned=event.lesson_learned,
        npt_hours=event.npt_hours,
        source_document=event.source_document,
        source_page=event.source_page,
        confidence=event.confidence,
        is_demo_data=event.is_demo_data,
        created_at=event.created_at,
        well_name=well.well_name if well else event.well_id
    )

@router.post("", response_model=DrillingEventSchema)
def create_event(
    data: DrillingEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_engineer)
):
    event_id = f"EVT-MAN-{int(db.query(DrillingEvent).count() + 1):04d}"
    new_event = DrillingEvent(
        event_id=event_id,
        well_id=data.well_id,
        event_type=data.event_type,
        start_depth=data.start_depth,
        end_depth=data.end_depth,
        formation=data.formation,
        severity=data.severity,
        cause=data.cause,
        impact=data.impact,
        mitigation=data.mitigation,
        lesson_learned=data.lesson_learned,
        npt_hours=data.npt_hours,
        source_document=data.source_document,
        source_page=data.source_page,
        confidence=data.confidence,
        is_demo_data=True
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event
