from sqlalchemy import Column, Integer, String, Float, Text, Boolean
from backend.app.core.database import Base

class Formation(Base):
    __tablename__ = "formations"

    formation_id = Column(String(50), primary_key=True, index=True)
    formation_name = Column(String(100), nullable=False, unique=True, index=True)
    lithology = Column(String(150), nullable=False) # Sandstone, Shale, Limestone, Siltstone, Clay
    age_era = Column(String(100), default="Tertiary") # Oligocene, Eocene, Miocene, Paleocene
    typical_top_depth = Column(Float, nullable=False) # Metres
    typical_bottom_depth = Column(Float, nullable=False) # Metres
    pore_pressure_gradient_sg = Column(Float, default=1.05) # Specific Gravity equivalent
    fracture_gradient_sg = Column(Float, default=1.65)
    known_hazards = Column(Text, default="Sloughing shale, partial losses, high torque")
    drillability_rating = Column(String(50), default="Medium") # Easy, Medium, Hard, Abrasive
    risk_level = Column(String(50), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    color_hex = Column(String(20), default="#D97706") # Geological column visualization color
    is_demo_data = Column(Boolean, default=True)


class Reservoir(Base):
    __tablename__ = "reservoirs"

    reservoir_id = Column(String(50), primary_key=True, index=True)
    reservoir_name = Column(String(100), nullable=False, index=True)
    formation_id = Column(String(50), index=True)
    fluid_type = Column(String(50), default="Oil & Associated Gas") # Light Oil, Heavy Oil, Gas, Condensate
    depth_top = Column(Float, nullable=False)
    depth_bottom = Column(Float, nullable=False)
    initial_pressure_psi = Column(Float, default=4500.0)
    temperature_c = Column(Float, default=115.0)
    porosity_pct = Column(Float, default=18.5)
    permeability_md = Column(Float, default=45.0)
    drive_mechanism = Column(String(100), default="Water Drive + Solution Gas")
    is_demo_data = Column(Boolean, default=True)
