from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.core.database import Base

class Well(Base):
    __tablename__ = "wells"

    well_id = Column(String(50), primary_key=True, index=True)
    well_name = Column(String(100), nullable=False, index=True)
    field = Column(String(100), nullable=False, default="Dikom-Chabua")
    block = Column(String(100), nullable=False, default="Dibrugarh ML")
    basin = Column(String(100), nullable=False, default="Assam-Arakan")
    operator = Column(String(100), nullable=False, default="OIL India Limited (Synthetic Prototype)")
    well_type = Column(String(50), default="Development") # Exploratory, Development, Delineation
    status = Column(String(50), default="Drilling") # Drilling, Completed, Suspended, Plugged & Abandoned
    target_depth = Column(Float, nullable=False, default=4200.0) # Metres
    current_depth = Column(Float, nullable=False, default=0.0) # Metres
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    spud_date = Column(String(50), default="2026-01-15")
    completion_date = Column(String(50), nullable=True)
    is_active_well = Column(Boolean, default=False, index=True)
    is_demo_data = Column(Boolean, default=True, nullable=False)
    data_source = Column(String(100), default="SYNTHETIC_GENERATED_DEMO", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    trajectories = relationship("WellTrajectory", back_populates="well", cascade="all, delete-orphan")
    parameters = relationship("DrillingParameter", back_populates="well", cascade="all, delete-orphan")
    events = relationship("DrillingEvent", back_populates="well", cascade="all, delete-orphan")
    casing_programs = relationship("Casing", back_populates="well", cascade="all, delete-orphan")
    cementing_programs = relationship("Cementing", back_populates="well", cascade="all, delete-orphan")
    mud_programs = relationship("MudProgram", back_populates="well", cascade="all, delete-orphan")


class WellTrajectory(Base):
    __tablename__ = "well_trajectories"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(String(50), ForeignKey("wells.well_id"), nullable=False, index=True)
    measured_depth = Column(Float, nullable=False) # MD in metres
    true_vertical_depth = Column(Float, nullable=False) # TVD in metres
    inclination = Column(Float, default=0.0) # Degrees
    azimuth = Column(Float, default=0.0) # Degrees
    dogleg_severity = Column(Float, default=0.0) # deg/30m
    easting = Column(Float, default=0.0)
    northing = Column(Float, default=0.0)

    well = relationship("Well", back_populates="trajectories")


class Casing(Base):
    __tablename__ = "casing_programs"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(String(50), ForeignKey("wells.well_id"), nullable=False, index=True)
    casing_type = Column(String(50), nullable=False) # Conductor, Surface, Intermediate, Production, Liner
    hole_size = Column(Float, nullable=False) # inches e.g. 17.5, 12.25, 8.5
    casing_size = Column(Float, nullable=False) # inches e.g. 13.375, 9.625, 7.0
    top_depth = Column(Float, default=0.0) # Metres
    shoe_depth = Column(Float, nullable=False) # Metres
    weight_ppf = Column(Float, default=47.0) # lb/ft
    grade = Column(String(50), default="L-80")
    is_demo_data = Column(Boolean, default=True)

    well = relationship("Well", back_populates="casing_programs")


class Cementing(Base):
    __tablename__ = "cementing_programs"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(String(50), ForeignKey("wells.well_id"), nullable=False, index=True)
    casing_type = Column(String(50), nullable=False)
    slurry_type = Column(String(100), default="Class G + Microfine")
    slurry_density_ppg = Column(Float, default=15.8)
    top_of_cement_depth = Column(Float, default=0.0) # Metres
    volume_bbls = Column(Float, default=250.0)
    pressure_psi = Column(Float, default=2200.0)
    remarks = Column(Text, nullable=True)
    is_demo_data = Column(Boolean, default=True)

    well = relationship("Well", back_populates="cementing_programs")


class MudProgram(Base):
    __tablename__ = "mud_programs"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(String(50), ForeignKey("wells.well_id"), nullable=False, index=True)
    from_depth = Column(Float, nullable=False)
    to_depth = Column(Float, nullable=False)
    mud_type = Column(String(100), default="Polymer WBM") # Spud Mud, Polymer WBM, KCL-Glycol, SOBM
    mud_weight_min = Column(Float, nullable=False) # Specific Gravity / SG (e.g. 1.08 - 1.35)
    mud_weight_max = Column(Float, nullable=False)
    viscosity = Column(Float, default=45.0) # seconds
    pv = Column(Float, default=16.0) # Plastic Viscosity cP
    yp = Column(Float, default=22.0) # Yield Point lb/100ft2
    ph = Column(Float, default=9.5)
    is_demo_data = Column(Boolean, default=True)

    well = relationship("Well", back_populates="mud_programs")
