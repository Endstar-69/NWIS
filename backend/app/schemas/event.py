from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DrillingEventCreate(BaseModel):
    well_id: str
    event_type: str
    start_depth: float
    end_depth: float
    formation: str
    severity: str = "HIGH"
    cause: str
    impact: str
    mitigation: str
    lesson_learned: str
    npt_hours: float = 12.0
    source_document: str = "Manual Entry"
    source_page: int = 1
    confidence: float = 1.0

class DrillingEventSchema(BaseModel):
    event_id: str
    well_id: str
    event_type: str
    start_depth: float
    end_depth: float
    formation: str
    severity: str
    cause: str
    impact: str
    mitigation: str
    lesson_learned: str
    npt_hours: float
    source_document: str
    source_page: int
    confidence: float
    is_demo_data: bool
    created_at: Optional[datetime] = None
    well_name: Optional[str] = None

    class Config:
        from_attributes = True

class EventFilterParams(BaseModel):
    well_id: Optional[str] = None
    formation: Optional[str] = None
    event_type: Optional[str] = None
    severity: Optional[str] = None
    min_depth: Optional[float] = None
    max_depth: Optional[float] = None
