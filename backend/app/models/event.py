from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.core.database import Base

class DrillingEvent(Base):
    __tablename__ = "drilling_events"

    event_id = Column(String(50), primary_key=True, index=True)
    well_id = Column(String(50), ForeignKey("wells.well_id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    # Types: MUD_LOSS, KICK, STUCK_PIPE, TORQUE_SPIKE, PACK_OFF, OVERPRESSURE,
    # WELL_CONTROL, FISHING, CEMENTING_ISSUE, LOST_CIRCULATION, NPT, CASING_ISSUE
    
    start_depth = Column(Float, nullable=False, index=True)
    end_depth = Column(Float, nullable=False)
    formation = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), default="HIGH", index=True) # LOW, MEDIUM, HIGH, CRITICAL
    
    # Detailed event analysis & institutional memory
    cause = Column(Text, nullable=False)
    impact = Column(Text, nullable=False)
    mitigation = Column(Text, nullable=False)
    lesson_learned = Column(Text, nullable=False)
    
    npt_hours = Column(Float, default=12.0)
    source_document = Column(String(150), default="W001_Final_Well_Report.pdf")
    source_page = Column(Integer, default=1)
    confidence = Column(Float, default=0.95) # Extraction confidence 0.0 - 1.0
    is_demo_data = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    well = relationship("Well", back_populates="events")
