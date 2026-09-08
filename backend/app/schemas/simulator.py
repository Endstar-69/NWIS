from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class ScenarioConfigureRequest(BaseModel):
    scenario_name: str = Field(
        ...,
        description="Target scenario to trigger: normal_drilling, lost_circulation, gas_kick_influx, or stuck_pipe_packoff."
    )
    duration_steps: Optional[int] = Field(
        default=60,
        ge=10,
        le=3600,
        description="Duration of scenario in simulator ticks before auto-resolution."
    )
    auto_resolve: Optional[bool] = Field(
        default=True,
        description="Whether the simulator automatically recovers to normal_drilling upon duration expiry."
    )


class ScenarioItem(BaseModel):
    id: str
    name: str
    description: str
    expected_anomalies: List[str]
    risk_tier: str


class TelemetryProvenance(BaseModel):
    classification: str = "[B] Realistic Physics-Based Simulation"
    generator: str = "NWIS ScenarioDrillingSimulator v2.0"
    scenario: str
    scenario_phase: str
    step: int
    scenario_step: int
    seed: Optional[int] = None
    physics_engine: str
    is_synthetic: bool = True
    disclaimer: str


class TelemetryResponse(BaseModel):
    well_id: str
    depth: float
    timestamp: str
    formation_name: str
    rop: float
    wob: float
    rpm: float
    torque: float
    standpipe_pressure: float
    flow_rate: float
    flow_in: float
    flow_out: float
    delta_flow: float
    pit_volume: float
    gas_units: float
    mud_weight: float
    ecd: float
    hook_load: float
    teale_mse_psi: float
    inclination: float
    azimuth: float
    is_simulated: bool = True
    is_demo_data: bool = True
    provenance: TelemetryProvenance
