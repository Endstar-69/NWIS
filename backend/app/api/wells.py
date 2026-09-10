from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.well import Well, WellTrajectory, Casing, Cementing, MudProgram
from backend.app.models.event import DrillingEvent
from backend.app.models.drilling import DrillingParameter
from backend.app.schemas.well import (
    WellResponse, NearbyWellResponse, WellComparisonItem,
    WellTrajectorySchema, CasingSchema, CementingSchema, MudProgramSchema
)
from backend.app.schemas.event import DrillingEventSchema
from backend.app.services.well_service import (
    get_all_wells, get_well_by_id, get_active_well, get_nearby_wells, compare_wells
)
from backend.app.api.auth import get_current_active_user

router = APIRouter(prefix="/wells", tags=["Wells"])

@router.get("", response_model=List[WellResponse])
def list_wells(
    field: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    wells = get_all_wells(db, limit=limit, offset=offset, field=field, is_active=is_active)
    res = []
    for w in wells:
        ev_count = db.query(DrillingEvent).filter(DrillingEvent.well_id == w.well_id).count()
        res.append(WellResponse(
            well_id=w.well_id,
            well_name=w.well_name,
            field=w.field,
            block=w.block,
            basin=w.basin,
            operator=w.operator,
            well_type=w.well_type,
            status=w.status,
            target_depth=w.target_depth,
            current_depth=w.current_depth,
            latitude=w.latitude,
            longitude=w.longitude,
            spud_date=w.spud_date,
            completion_date=w.completion_date,
            is_active_well=w.is_active_well,
            is_demo_data=w.is_demo_data,
            data_source=w.data_source,
            created_at=w.created_at,
            events_count=ev_count
        ))
    return res

@router.get("/active", response_model=WellResponse)
def get_current_active_well(db: Session = Depends(get_db)):
    active = get_active_well(db)
    if not active:
        raise HTTPException(status_code=404, detail="No active well found")
    ev_count = db.query(DrillingEvent).filter(DrillingEvent.well_id == active.well_id).count()
    return WellResponse(
        well_id=active.well_id,
        well_name=active.well_name,
        field=active.field,
        block=active.block,
        basin=active.basin,
        operator=active.operator,
        well_type=active.well_type,
        status=active.status,
        target_depth=active.target_depth,
        current_depth=active.current_depth,
        latitude=active.latitude,
        longitude=active.longitude,
        spud_date=active.spud_date,
        completion_date=active.completion_date,
        is_active_well=active.is_active_well,
        is_demo_data=active.is_demo_data,
        data_source=active.data_source,
        created_at=active.created_at,
        events_count=ev_count
    )

@router.get("/compare", response_model=List[WellComparisonItem])
def compare_selected_wells(
    well_ids: List[str] = Query(..., description="List of well IDs to compare"),
    db: Session = Depends(get_db)
):
    return compare_wells(db, well_ids)

@router.get("/{well_id}", response_model=WellResponse)
def get_well_details(well_id: str, db: Session = Depends(get_db)):
    well = get_well_by_id(db, well_id)
    if not well:
        raise HTTPException(status_code=404, detail=f"Well '{well_id}' not found")
    ev_count = db.query(DrillingEvent).filter(DrillingEvent.well_id == well_id).count()
    return WellResponse(
        well_id=well.well_id,
        well_name=well.well_name,
        field=well.field,
        block=well.block,
        basin=well.basin,
        operator=well.operator,
        well_type=well.well_type,
        status=well.status,
        target_depth=well.target_depth,
        current_depth=well.current_depth,
        latitude=well.latitude,
        longitude=well.longitude,
        spud_date=well.spud_date,
        completion_date=well.completion_date,
        is_active_well=well.is_active_well,
        is_demo_data=well.is_demo_data,
        data_source=well.data_source,
        created_at=well.created_at,
        events_count=ev_count
    )

@router.get("/{well_id}/nearby", response_model=List[NearbyWellResponse])
def get_nearby_wells_endpoint(
    well_id: str,
    radius_km: float = Query(25.0, description="Search radius in kilometers"),
    min_similarity: float = Query(0.0, description="Minimum similarity percentage"),
    db: Session = Depends(get_db)
):
    return get_nearby_wells(db, well_id, radius_km=radius_km, min_similarity=min_similarity)

@router.get("/{well_id}/events", response_model=List[DrillingEventSchema])
def get_well_historical_events(well_id: str, db: Session = Depends(get_db)):
    events = db.query(DrillingEvent).filter(DrillingEvent.well_id == well_id).all()
    well = get_well_by_id(db, well_id)
    w_name = well.well_name if well else well_id
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
            well_name=w_name
        ))
    return res

@router.get("/{well_id}/incidents", response_model=List[DrillingEventSchema])
def get_well_incidents(
    well_id: str,
    severity: Optional[str] = Query(None, description="Optional severity filter (e.g., HIGH, CRITICAL)"),
    db: Session = Depends(get_db)
):
    """Returns drilling incidents for a specific well, optionally filtered by severity."""
    query = db.query(DrillingEvent).filter(DrillingEvent.well_id == well_id)
    if severity:
        query = query.filter(DrillingEvent.severity == severity.upper())
    else:
        # Default to all recorded incidents or hazards
        query = query.filter(DrillingEvent.severity.in_(["MEDIUM", "HIGH", "CRITICAL"]))
    
    events = query.order_by(DrillingEvent.start_depth.asc()).all()
    well = get_well_by_id(db, well_id)
    w_name = well.well_name if well else well_id
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
            well_name=w_name
        ))
    return res

@router.get("/{well_id}/trajectory", response_model=List[WellTrajectorySchema])
def get_well_trajectory_endpoint(well_id: str, db: Session = Depends(get_db)):
    return db.query(WellTrajectory).filter(WellTrajectory.well_id == well_id).order_by(WellTrajectory.measured_depth.asc()).all()

@router.get("/{well_id}/telemetry-history")
def get_well_telemetry_history(
    well_id: str,
    limit: int = 150,
    db: Session = Depends(get_db)
):
    params = db.query(DrillingParameter).filter(
        DrillingParameter.well_id == well_id
    ).order_by(DrillingParameter.depth.desc()).limit(limit).all()
    params.reverse() # Chronological order
    return params
