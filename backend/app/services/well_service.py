from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.well import Well, WellTrajectory, Casing, Cementing, MudProgram
from backend.app.models.event import DrillingEvent
from backend.app.models.formation import Formation, Reservoir
from backend.app.schemas.well import NearbyWellResponse, WellResponse, SimilarityBreakdown, WellComparisonItem, FormationSchema
from backend.app.services.similarity_service import haversine_distance, calculate_multi_factor_similarity

def get_all_wells(db: Session, limit: int = 100, offset: int = 0, field: Optional[str] = None, is_active: Optional[bool] = None) -> List[Well]:
    query = db.query(Well)
    if field:
        query = query.filter(Well.field.ilike(f"%{field}%"))
    if is_active is not None:
        query = query.filter(Well.is_active_well == is_active)
    return query.offset(offset).limit(limit).all()

def get_well_by_id(db: Session, well_id: str) -> Optional[Well]:
    return db.query(Well).filter(Well.well_id == well_id).first()

def get_active_well(db: Session) -> Optional[Well]:
    active = db.query(Well).filter(Well.is_active_well == True).first()
    if not active:
        active = db.query(Well).first()
    return active

def get_nearby_wells(db: Session, well_id: str, radius_km: float = 25.0, min_similarity: float = 0.0) -> List[NearbyWellResponse]:
    target_well = get_well_by_id(db, well_id)
    if not target_well:
        return []

    target_events = db.query(DrillingEvent).filter(DrillingEvent.well_id == well_id).all()
    all_other_wells = db.query(Well).filter(Well.well_id != well_id).all()
    all_formations = db.query(Formation).order_by(Formation.typical_top_depth.asc()).all()
    all_reservoirs = db.query(Reservoir).all()

    nearby_list = []
    for other in all_other_wells:
        dist = haversine_distance(target_well.latitude, target_well.longitude, other.latitude, other.longitude)
        if dist <= radius_km:
            other_events = db.query(DrillingEvent).filter(DrillingEvent.well_id == other.well_id).all()
            sim_score, sim_breakdown = calculate_multi_factor_similarity(
                target_well, other, dist, target_events, other_events,
                max_radius_km=max(radius_km, 50.0),
                formations=all_formations,
                reservoirs=all_reservoirs
            )

            if sim_score >= min_similarity:
                # Determine risk level based on offset well historical events
                high_sev_count = sum(1 for e in other_events if e.severity in ["HIGH", "CRITICAL"])
                if high_sev_count >= 3:
                    risk_lvl = "CRITICAL"
                elif high_sev_count >= 1:
                    risk_lvl = "HIGH"
                elif len(other_events) > 0:
                    risk_lvl = "MEDIUM"
                else:
                    risk_lvl = "LOW"

                common_formations = sim_breakdown.get("common_formations") or list({e.formation for e in other_events if e.formation})

                nearby_list.append(NearbyWellResponse(
                    well=WellResponse(
                        well_id=other.well_id,
                        well_name=other.well_name,
                        field=other.field,
                        block=other.block,
                        basin=other.basin,
                        operator=other.operator,
                        well_type=other.well_type,
                        status=other.status,
                        target_depth=other.target_depth,
                        current_depth=other.current_depth,
                        latitude=other.latitude,
                        longitude=other.longitude,
                        spud_date=other.spud_date,
                        completion_date=other.completion_date,
                        is_active_well=other.is_active_well,
                        is_demo_data=other.is_demo_data,
                        data_source=other.data_source,
                        created_at=other.created_at,
                        events_count=len(other_events)
                    ),
                    distance_km=dist,
                    similarity_score=sim_score,
                    similarity_breakdown=SimilarityBreakdown(**sim_breakdown),
                    risk_level=risk_lvl,
                    historical_events_count=len(other_events),
                    common_formations=common_formations
                ))

    # Sort primarily by proximity, then similarity score
    nearby_list.sort(key=lambda x: x.distance_km)
    return nearby_list

def compare_wells(db: Session, well_ids: List[str]) -> List[WellComparisonItem]:
    comparison_items = []
    all_formations = db.query(Formation).all()
    fmt_schemas = [FormationSchema.model_validate(f) for f in all_formations]

    for w_id in well_ids:
        well = get_well_by_id(db, w_id)
        if not well:
            continue

        events = db.query(DrillingEvent).filter(DrillingEvent.well_id == w_id).all()
        casings = db.query(Casing).filter(Casing.well_id == w_id).all()
        cementings = db.query(Cementing).filter(Cementing.well_id == w_id).all()
        muds = db.query(MudProgram).filter(MudProgram.well_id == w_id).all()

        total_npt = sum(e.npt_hours for e in events)

        events_summary = [
            {
                "event_id": e.event_id,
                "event_type": e.event_type,
                "depth": e.start_depth,
                "formation": e.formation,
                "severity": e.severity,
                "npt_hours": e.npt_hours,
                "mitigation": e.mitigation
            }
            for e in events
        ]

        comparison_items.append(WellComparisonItem(
            well=WellResponse(
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
                events_count=len(events)
            ),
            formations=fmt_schemas,
            casing=[c for c in casings],
            cementing=[cm for cm in cementings],
            mud_program=[m for m in muds],
            events_summary=events_summary,
            total_npt_hours=round(total_npt, 1)
        ))

    return comparison_items
