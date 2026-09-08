"""
NWIS Telemetry Simulator Control API — Phase 2 Implementation.

CLASSIFICATION: [B] Realistic Physics-Based Simulation.
Provides endpoints for monitoring, configuring, and triggering scenario-driven drilling telemetry.
Strict RBAC enforced:
  - Read endpoints (status, scenarios): Available to all authenticated roles (Viewer+).
  - Write endpoints (configure, reset, tick): Restricted to Drilling Engineer and Admin.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any

from backend.app.api.auth import get_current_user, require_engineer
from backend.app.models.user import User
from backend.app.schemas.simulator import (
    ScenarioConfigureRequest,
    ScenarioItem,
    TelemetryResponse,
)
from simulator.drilling_stream import simulator_instance

router = APIRouter(prefix="/simulator", tags=["Drilling Telemetry Simulator"])


@router.get("/status")
def get_simulator_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Returns current simulator execution state, active scenario, phase, and provenance metadata.
    Accessible to all authenticated users.
    """
    return simulator_instance.get_scenario_status()


@router.get("/scenarios", response_model=List[ScenarioItem])
def list_available_scenarios(
    current_user: User = Depends(get_current_user)
) -> List[ScenarioItem]:
    """
    Returns catalogue of all supported drilling anomaly and normal scenarios.
    Accessible to all authenticated users.
    """
    return [ScenarioItem(**s) for s in simulator_instance.get_available_scenarios()]


@router.post("/configure")
def configure_simulator_scenario(
    request: ScenarioConfigureRequest,
    current_user: User = Depends(require_engineer)
) -> Dict[str, Any]:
    """
    Configures simulator to transition into a specific drilling scenario.
    Requires Drilling Engineer role or higher.
    """
    try:
        res = simulator_instance.set_scenario(
            scenario_name=request.scenario_name,
            duration_steps=request.duration_steps or 60,
            auto_resolve=request.auto_resolve if request.auto_resolve is not None else True
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/reset")
def reset_simulator_to_normal(
    current_user: User = Depends(require_engineer)
) -> Dict[str, Any]:
    """
    Resets the simulator back to normal steady-state drilling.
    Requires Drilling Engineer role or higher.
    """
    return simulator_instance.reset_to_normal()


@router.post("/tick", response_model=TelemetryResponse)
def manual_simulator_tick(
    current_user: User = Depends(require_engineer)
) -> TelemetryResponse:
    """
    Executes a single simulation tick manually and returns the resulting telemetry packet.
    Requires Drilling Engineer role or higher.
    """
    telemetry_data = simulator_instance.tick()
    return TelemetryResponse(**telemetry_data)
