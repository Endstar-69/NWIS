from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class WellTrajectorySchema(BaseModel):
    id: Optional[int] = None
    measured_depth: float
    true_vertical_depth: float
    inclination: float
    azimuth: float
    dogleg_severity: float
    easting: float
    northing: float

    class Config:
        from_attributes = True

class CasingSchema(BaseModel):
    id: Optional[int] = None
    casing_type: str
    hole_size: float
    casing_size: float
    top_depth: float
    shoe_depth: float
    weight_ppf: float
    grade: str

    class Config:
        from_attributes = True

class CementingSchema(BaseModel):
    id: Optional[int] = None
    casing_type: str
    slurry_type: str
    slurry_density_ppg: float
    top_of_cement_depth: float
    volume_bbls: float
    pressure_psi: float
    remarks: Optional[str] = None

    class Config:
        from_attributes = True

class MudProgramSchema(BaseModel):
    id: Optional[int] = None
    from_depth: float
    to_depth: float
    mud_type: str
    mud_weight_min: float
    mud_weight_max: float
    viscosity: float
    pv: float
    yp: float
    ph: float

    class Config:
        from_attributes = True

class WellBase(BaseModel):
    well_id: str
    well_name: str
    field: str
    block: str
    basin: str
    operator: str
    well_type: str
    status: str
    target_depth: float
    current_depth: float
    latitude: float
    longitude: float
    spud_date: str
    completion_date: Optional[str] = None
    is_active_well: bool = False
    is_demo_data: bool = True
    data_source: str = "SYNTHETIC_GENERATED_DEMO"

class WellResponse(WellBase):
    created_at: Optional[datetime] = None
    events_count: Optional[int] = 0

    class Config:
        from_attributes = True

class SimilarityBreakdown(BaseModel):
    distance_score: float # 0.0 - 1.0
    formation_score: float # 0.0 - 1.0
    depth_score: float # 0.0 - 1.0
    reservoir_score: float # 0.0 - 1.0
    trajectory_score: float # 0.0 - 1.0
    events_score: float # 0.0 - 1.0
    weights_used: dict
    common_formations: Optional[List[str]] = None
    formula: Optional[str] = None
    method_details: Optional[dict] = None
    provenance: Optional[dict] = None

class NearbyWellResponse(BaseModel):
    well: WellResponse
    distance_km: float
    similarity_score: float # 0 - 100%
    similarity_breakdown: SimilarityBreakdown
    risk_level: str # LOW, MEDIUM, HIGH, CRITICAL
    historical_events_count: int
    common_formations: List[str]

class FormationSchema(BaseModel):
    formation_id: str
    formation_name: str
    lithology: str
    age_era: str
    typical_top_depth: float
    typical_bottom_depth: float
    pore_pressure_gradient_sg: float
    fracture_gradient_sg: float
    known_hazards: str
    drillability_rating: str
    risk_level: str
    color_hex: str

    class Config:
        from_attributes = True

class WellComparisonItem(BaseModel):
    well: WellResponse
    formations: List[FormationSchema]
    casing: List[CasingSchema]
    cementing: List[CementingSchema]
    mud_program: List[MudProgramSchema]
    events_summary: List[dict]
    total_npt_hours: float
