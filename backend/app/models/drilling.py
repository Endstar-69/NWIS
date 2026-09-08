from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.core.database import Base

class DrillingRun(Base):
    __tablename__ = "drilling_runs"

    run_id = Column(String(50), primary_key=True, index=True)
    well_id = Column(String(50), ForeignKey("wells.well_id"), nullable=False, index=True)
    run_number = Column(Integer, default=1)
    bit_number = Column(String(50), default="RR1")
    bit_size = Column(Float, nullable=False, default=8.5) # Inches
    bit_type = Column(String(50), default="PDC 5-blade") # PDC, Tricone, Hybrid
    run_from_depth = Column(Float, nullable=False)
    run_to_depth = Column(Float, nullable=False)
    hours_drilled = Column(Float, default=48.0)
    avg_rop = Column(Float, default=12.5) # m/hr
    bha_description = Column(String(255), default="Bit + Motor + MWD + LWD + HWDP + DP")
    is_demo_data = Column(Boolean, default=True)


class DrillingParameter(Base):
    __tablename__ = "drilling_parameters"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(String(50), ForeignKey("wells.well_id"), nullable=False, index=True)
    depth = Column(Float, nullable=False, index=True) # Metres
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Telemetry parameters
    rop = Column(Float, nullable=False) # Rate of Penetration (m/hr)
    wob = Column(Float, nullable=False) # Weight on Bit (kdaN / tons)
    rpm = Column(Float, nullable=False) # Rotary Speed (RPM)
    torque = Column(Float, nullable=False) # Torque (kNm / ft-lbs)
    standpipe_pressure = Column(Float, nullable=False) # SPP (psi / bar)
    flow_rate = Column(Float, nullable=False) # Mud Flow Rate (LPM / gpm)
    mud_weight = Column(Float, nullable=False) # Mud Density (SG / ppg)
    ecd = Column(Float, nullable=False) # Equivalent Circulating Density (SG / ppg)
    hook_load = Column(Float, nullable=False) # Hook Load (tons / klbs)
    
    # Directional & Geological context
    inclination = Column(Float, default=0.0)
    azimuth = Column(Float, default=0.0)
    formation_name = Column(String(100), default="Barail Sand")
    hole_size = Column(Float, default=8.5)
    bit_type = Column(String(50), default="PDC")
    is_simulated = Column(Boolean, default=False)
    is_demo_data = Column(Boolean, default=True)

    well = relationship("Well", back_populates="parameters")
