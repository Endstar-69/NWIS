"""
NWIS Automated Test Suite — Phase 2: Data Provenance & Scenario-Driven Telemetry Simulation.

CLASSIFICATION: [A] Real Implementation (Test Suite) testing [B] Physics-Based Simulation.

Test Coverage:
  1. normal_drilling: Gaussian stationarity, balanced hydraulics, provenance metadata.
  2. lost_circulation: Flow out < Flow in, SPP drop, pit volume depletion.
  3. gas_kick_influx: Flow out > Flow in, pit volume gain, gas units surge, drilling break.
  4. stuck_pipe_packoff: Erratic torque surge, RPM stall, SPP pack-off spike, hookload overpull.
  5. Scenario auto-recovery to normal_drilling upon expiration.
  6. Provenance metadata structure, explicit [B] classification, and disclaimer tag.
  7. Simulator REST API: 401 for unauthenticated, 403 for Viewer mutating state, 200 for Engineer/Admin.
  8. Simulator API invalid scenario 400 Bad Request validation.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from simulator.drilling_stream import DrillingStreamSimulator, simulator_instance

client = TestClient(app)


# ── 1. Unit Tests for Simulation Physics & Signatures ─────────────────────────

def test_normal_drilling_scenario():
    """Validates baseline steady-state drilling parameters and stationarity."""
    sim = DrillingStreamSimulator(well_id="TEST-WELL-NORMAL", start_depth=3400.0, seed=123)
    sim.set_scenario("normal_drilling")

    packets = [sim.tick() for _ in range(10)]
    last = packets[-1]

    # Verification of physical stationarity
    assert 3400.0 < last["depth"] < 3405.0
    assert 13.0 <= last["wob"] <= 17.0
    assert 100.0 <= last["rpm"] <= 120.0
    assert 10.0 <= last["torque"] <= 18.0
    assert 2200.0 <= last["standpipe_pressure"] <= 2500.0
    # Delta flow in normal drilling stays near zero
    assert abs(last["delta_flow"]) < 30.0
    # Teale MSE computed and bounded
    assert 5000.0 <= last["teale_mse_psi"] <= 500000.0

    # Provenance metadata disclosure
    assert "provenance" in last
    prov = last["provenance"]
    assert prov["classification"] == "[B] Realistic Physics-Based Simulation"
    assert prov["scenario"] == "normal_drilling"
    assert prov["is_synthetic"] is True
    assert "disclaimer" in prov


def test_lost_circulation_signature():
    """Validates physical signature of lost circulation: SPP drop, returns drop, pit depletion."""
    sim = DrillingStreamSimulator(well_id="TEST-WELL-LOSS", start_depth=3420.0, seed=456)
    sim.set_scenario("lost_circulation", duration_steps=40, auto_resolve=True)

    initial_pit = sim.pit_volume
    # Run into full development phase (step > 10)
    for _ in range(18):
        pkt = sim.tick()

    # In full development of lost circulation:
    # 1. Flow Out must be significantly less than Flow In (negative delta flow)
    assert pkt["delta_flow"] < -150.0
    assert pkt["flow_out"] < pkt["flow_in"]
    # 2. Standpipe pressure drops due to loss of annular hydrostatic column
    assert pkt["standpipe_pressure"] < 2250.0
    # 3. Surface pit volume decreases
    assert pkt["pit_volume"] < initial_pit
    # 4. Provenance is correctly tagged
    assert pkt["provenance"]["scenario"] == "lost_circulation"
    assert pkt["provenance"]["scenario_phase"] in ["onset", "full_development"]


def test_gas_kick_influx_signature():
    """Validates physical signature of gas kick: drilling break, positive delta flow, pit gain, gas spike."""
    sim = DrillingStreamSimulator(well_id="TEST-WELL-KICK", start_depth=3450.0, seed=789)
    sim.set_scenario("gas_kick_influx", duration_steps=40, auto_resolve=True)

    initial_pit = sim.pit_volume
    for _ in range(18):
        pkt = sim.tick()

    # In full development of gas kick influx:
    # 1. Flow Out exceeds Flow In (positive delta flow)
    assert pkt["delta_flow"] > 100.0
    assert pkt["flow_out"] > pkt["flow_in"]
    # 2. Pit volume gains due to influx volume
    assert pkt["pit_volume"] > initial_pit
    # 3. Gas units in mud returns surge drastically
    assert pkt["gas_units"] > 200.0
    # 4. Drilling break (ROP elevated)
    assert pkt["rop"] > 12.0
    # 5. Provenance is correctly tagged
    assert pkt["provenance"]["scenario"] == "gas_kick_influx"


def test_stuck_pipe_packoff_signature():
    """Validates physical signature of stuck pipe pack-off: torque surge, RPM stall, SPP spike."""
    sim = DrillingStreamSimulator(well_id="TEST-WELL-STUCK", start_depth=3430.0, seed=101)
    sim.set_scenario("stuck_pipe_packoff", duration_steps=40, auto_resolve=True)

    for _ in range(18):
        pkt = sim.tick()

    # In full development of pack-off / sticking:
    # 1. Torque surges with erratic resistance
    assert pkt["torque"] > 20.0
    # 2. String RPM stalls or drops severely
    assert pkt["rpm"] < 80.0
    # 3. Standpipe pressure spikes as annular cuttings pack off circulation
    assert pkt["standpipe_pressure"] > 2500.0
    # 4. Hook load overpull elevated
    assert pkt["hook_load"] > 130.0
    # 5. Provenance is correctly tagged
    assert pkt["provenance"]["scenario"] == "stuck_pipe_packoff"


def test_scenario_auto_recovery():
    """Validates that simulator automatically recovers to normal_drilling after duration expires."""
    sim = DrillingStreamSimulator(well_id="TEST-WELL-RECOVERY", start_depth=3400.0, seed=202)
    sim.set_scenario("lost_circulation", duration_steps=12, auto_resolve=True)

    assert sim.current_scenario == "lost_circulation"

    # Step past max_scenario_steps
    for _ in range(14):
        sim.tick()

    # Simulator should automatically have transitioned back to normal_drilling
    assert sim.current_scenario == "normal_drilling"
    assert sim.scenario_phase == "baseline"


# ── 2. Integration & RBAC Tests for Simulator API ────────────────────────────

def test_unauthenticated_simulator_routes_return_401():
    """Simulator routes must reject unauthenticated requests with HTTP 401."""
    assert client.get("/api/simulator/status").status_code == 401
    assert client.get("/api/simulator/scenarios").status_code == 401
    assert client.post("/api/simulator/configure", json={"scenario_name": "lost_circulation"}).status_code == 401
    assert client.post("/api/simulator/reset").status_code == 401
    assert client.post("/api/simulator/tick").status_code == 401


def test_viewer_can_read_simulator_status_and_scenarios(viewer_headers):
    """Viewer role is permitted to monitor status and list available scenarios."""
    status_res = client.get("/api/simulator/status", headers=viewer_headers)
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert "current_scenario" in status_data
    assert "classification" in status_data
    assert status_data["classification"] == "[B] Realistic Physics-Based Simulation"

    scenarios_res = client.get("/api/simulator/scenarios", headers=viewer_headers)
    assert scenarios_res.status_code == 200
    scenarios_list = scenarios_res.json()
    scenario_ids = [s["id"] for s in scenarios_list]
    assert "normal_drilling" in scenario_ids
    assert "lost_circulation" in scenario_ids
    assert "gas_kick_influx" in scenario_ids
    assert "stuck_pipe_packoff" in scenario_ids


def test_viewer_cannot_configure_simulator(viewer_headers):
    """Viewer role must receive HTTP 403 Forbidden when attempting to mutate simulation."""
    res = client.post(
        "/api/simulator/configure",
        json={"scenario_name": "lost_circulation", "duration_steps": 30},
        headers=viewer_headers
    )
    assert res.status_code == 403

    res_reset = client.post("/api/simulator/reset", headers=viewer_headers)
    assert res_reset.status_code == 403

    res_tick = client.post("/api/simulator/tick", headers=viewer_headers)
    assert res_tick.status_code == 403


def test_driller_can_configure_and_tick_simulator(driller_headers):
    """Drilling Engineer role is authorized to configure scenarios and advance ticks."""
    # 1. Configure to gas_kick_influx
    config_res = client.post(
        "/api/simulator/configure",
        json={"scenario_name": "gas_kick_influx", "duration_steps": 50, "auto_resolve": True},
        headers=driller_headers
    )
    assert config_res.status_code == 200
    assert config_res.json()["scenario"] == "gas_kick_influx"

    # 2. Execute manual tick
    tick_res = client.post("/api/simulator/tick", headers=driller_headers)
    assert tick_res.status_code == 200
    tick_data = tick_res.json()
    assert tick_data["well_id"] == "WELL-001"
    assert "provenance" in tick_data
    assert tick_data["provenance"]["scenario"] == "gas_kick_influx"
    assert tick_data["provenance"]["classification"] == "[B] Realistic Physics-Based Simulation"

    # 3. Reset back to normal
    reset_res = client.post("/api/simulator/reset", headers=driller_headers)
    assert reset_res.status_code == 200
    assert reset_res.json()["scenario"] == "normal_drilling"


def test_invalid_scenario_configuration_returns_400(driller_headers):
    """Attempting to trigger an unknown scenario returns HTTP 400 Bad Request."""
    res = client.post(
        "/api/simulator/configure",
        json={"scenario_name": "unsupported_fantasy_scenario"},
        headers=driller_headers
    )
    assert res.status_code == 400
    assert "Unknown scenario" in res.json()["detail"]
