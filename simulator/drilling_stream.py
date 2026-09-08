"""
NWIS Drilling Telemetry Simulator — Phase 2 Implementation.

CLASSIFICATION: [B] Realistic Physics-Based Simulation.
All data produced is synthetically generated using physical models and empirical correlations.
Every telemetry packet includes full provenance metadata disclosing its synthetic origin.

Supported Scenarios:
  1. normal_drilling: Stationary Gaussian parameters around nominal baseline with depth drift.
  2. lost_circulation: Progressive thief-zone loss with SPP drop, Flow Out < Flow In, and pit volume depletion.
  3. gas_kick_influx: Wellbore influx with drilling break, Flow Out > Flow In, pit gain, and gas units spike.
  4. stuck_pipe_packoff: Cuttings bed accumulation / mechanical sticking with torque surge, RPM drop, and SPP spike.
"""

import math
import random
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import numpy as np

# Stratigraphic column with representative depths for Assam-Arakan reference basin
FORMATION_HORIZONS = [
    (1100.0, "Dhekiajuli Sandstone"),
    (1950.0, "Girujan Clay"),
    (2750.0, "Tipam Sandstone"),
    (3150.0, "Bokabil Formation"),
    (3700.0, "Barail Sandstone"),
    (3950.0, "Barail Coal-Shale"),
    (4350.0, "Kopili Formation"),
    (9999.0, "Sylhet Limestone"),
]

SCENARIO_CONFIGS = {
    "normal_drilling": {
        "description": "Steady-state rotary drilling in competent formation with balanced hydraulics and stable pit volume.",
        "expected_anomalies": [],
        "risk_tier": "LOW",
    },
    "lost_circulation": {
        "description": "Sub-surface fracture penetration causing mud loss, pit level drop, standpipe pressure decrease, and negative delta-flow.",
        "expected_anomalies": ["MUD_LOSS", "LOST_CIRCULATION"],
        "risk_tier": "CRITICAL",
    },
    "gas_kick_influx": {
        "description": "Permeable high-pressure gas sand influx resulting in drilling break, positive delta-flow, pit volume gain, and gas unit spike.",
        "expected_anomalies": ["KICK", "WELL_CONTROL"],
        "risk_tier": "CRITICAL",
    },
    "stuck_pipe_packoff": {
        "description": "Inadequate hole cleaning causing annular cuttings pack-off, erratic torque surges, RPM stall, and standpipe pressure escalation.",
        "expected_anomalies": ["STUCK_PIPE", "TORQUE_SPIKE", "PACK_OFF"],
        "risk_tier": "CRITICAL",
    },
}


class DrillingStreamSimulator:
    """
    Realistic physics-grounded drilling telemetry simulator.
    Exposes configurable drilling scenarios with Gaussian noise, hydrostatic drift,
    dynamic progression, and explicit synthetic provenance metadata.
    """

    def __init__(
        self,
        well_id: str = "WELL-001",
        start_depth: float = 3415.0,
        seed: Optional[int] = 42,
    ):
        self.well_id = well_id
        self.current_depth = float(start_depth)
        self.step = 0
        self.seed = seed
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

        # Baseline physical state
        self.bit_hours = 38.5
        self.nominal_rop = 9.5
        self.nominal_wob = 15.0
        self.nominal_rpm = 110.0
        self.nominal_torque = 13.0
        self.nominal_spp = 2350.0
        self.nominal_flow_in = 1950.0
        self.mud_weight = 1.28  # SG
        self.nominal_ecd = 1.33  # SG
        self.pit_volume = 120.0  # m3

        # Scenario management state
        self.current_scenario = "normal_drilling"
        self.scenario_step = 0
        self.max_scenario_steps = 60
        self.scenario_phase = "baseline"
        self.auto_resolve = True

        # Last generated telemetry state
        self.rop = self.nominal_rop
        self.wob = self.nominal_wob
        self.rpm = self.nominal_rpm
        self.torque = self.nominal_torque
        self.spp = self.nominal_spp
        self.flow_in = self.nominal_flow_in
        self.flow_out = self.nominal_flow_in
        self.delta_flow = 0.0
        self.ecd = self.nominal_ecd
        self.hook_load = 115.0
        self.gas_units = 25.0
        self.formation = "Barail Sandstone"

    def set_scenario(
        self,
        scenario_name: str,
        duration_steps: int = 60,
        auto_resolve: bool = True,
    ) -> Dict[str, Any]:
        """Configures the simulator to transition into a specific operational scenario."""
        if scenario_name not in SCENARIO_CONFIGS:
            raise ValueError(
                f"Unknown scenario '{scenario_name}'. Allowed: {list(SCENARIO_CONFIGS.keys())}"
            )
        self.current_scenario = scenario_name
        self.scenario_step = 0
        self.max_scenario_steps = max(10, duration_steps)
        self.scenario_phase = "onset" if scenario_name != "normal_drilling" else "baseline"
        self.auto_resolve = auto_resolve

        return {
            "status": "CONFIGURED",
            "scenario": self.current_scenario,
            "phase": self.scenario_phase,
            "duration_steps": self.max_scenario_steps,
            "auto_resolve": self.auto_resolve,
            "description": SCENARIO_CONFIGS[scenario_name]["description"],
        }

    def reset_to_normal(self) -> Dict[str, Any]:
        """Resets the simulator back to normal steady-state drilling."""
        return self.set_scenario("normal_drilling", duration_steps=60, auto_resolve=True)

    def get_scenario_status(self) -> Dict[str, Any]:
        """Returns the current simulation state and scenario progress."""
        return {
            "current_scenario": self.current_scenario,
            "scenario_phase": self.scenario_phase,
            "scenario_step": self.scenario_step,
            "max_scenario_steps": self.max_scenario_steps,
            "total_steps": self.step,
            "current_depth": self.current_depth,
            "formation": self.formation,
            "auto_resolve": self.auto_resolve,
            "classification": "[B] Realistic Physics-Based Simulation",
            "scenario_metadata": SCENARIO_CONFIGS.get(self.current_scenario, {}),
        }

    @staticmethod
    def get_available_scenarios() -> List[Dict[str, Any]]:
        """Lists all supported scenarios with their physical signatures."""
        return [
            {
                "id": k,
                "name": k.replace("_", " ").title(),
                "description": v["description"],
                "expected_anomalies": v["expected_anomalies"],
                "risk_tier": v["risk_tier"],
            }
            for k, v in SCENARIO_CONFIGS.items()
        ]

    def _determine_formation(self, depth: float) -> str:
        """Determines the geological formation based on TVD depth."""
        for limit_depth, formation_name in FORMATION_HORIZONS:
            if depth <= limit_depth:
                return formation_name
        return "Sylhet Limestone"

    def _update_scenario_phase(self):
        """Advances the internal lifecycle phase of an anomaly scenario."""
        if self.current_scenario == "normal_drilling":
            self.scenario_phase = "baseline"
            return

        progress = self.scenario_step / float(self.max_scenario_steps)
        if progress < 0.20:
            self.scenario_phase = "onset"
        elif progress < 0.75:
            self.scenario_phase = "full_development"
        elif progress < 1.0:
            self.scenario_phase = "stabilizing"
        else:
            if self.auto_resolve:
                self.current_scenario = "normal_drilling"
                self.scenario_phase = "baseline"
                self.scenario_step = 0
            else:
                self.scenario_phase = "critical_hold"

    def tick(self) -> Dict[str, Any]:
        """
        Advances the simulation by 1 timestep and returns the new telemetry packet.
        Incorporates Gaussian noise, drift, scenario signatures, and provenance metadata.
        """
        self.step += 1
        self.scenario_step += 1
        self._update_scenario_phase()

        # 1. Depth progression (ROP-dependent)
        # 1 tick ≈ 2-5 seconds of real drilling time -> 0.05 to 0.35 m
        delta_d = random.uniform(0.10, 0.30)
        self.current_depth = round(self.current_depth + delta_d, 2)
        self.formation = self._determine_formation(self.current_depth)

        # 2. Physics drift based on depth
        # String weight increases with depth (~32 kg/m)
        depth_drift_hookload = (self.current_depth / 1000.0) * 32.0
        # Friction/torque slightly drifts with depth
        depth_drift_torque = (self.current_depth / 1000.0) * 0.85
        # Hydrostatic backpressure drifts standpipe pressure slightly
        depth_drift_spp = (self.current_depth / 1000.0) * 25.0

        # Base nominal values with Gaussian sensor noise
        wob_noise = float(np.random.normal(0, 0.4))
        rpm_noise = float(np.random.normal(0, 1.2))
        spp_noise = float(np.random.normal(0, 12.0))
        flow_noise = float(np.random.normal(0, 10.0))
        torque_noise = float(np.random.normal(0, 0.35))
        hookload_noise = float(np.random.normal(0, 0.8))

        wob = max(4.0, self.nominal_wob + wob_noise)
        rpm = max(40.0, self.nominal_rpm + rpm_noise)
        spp = self.nominal_spp + depth_drift_spp + spp_noise
        flow_in = self.nominal_flow_in + flow_noise
        flow_out = flow_in + float(np.random.normal(0, 8.0))
        torque = self.nominal_torque + depth_drift_torque + torque_noise
        hook_load = 110.0 + depth_drift_hookload + hookload_noise
        rop = max(2.0, self.nominal_rop + float(np.random.normal(0, 0.5)))
        ecd = self.nominal_ecd
        gas_units = max(10.0, 25.0 + float(np.random.normal(0, 2.5)))

        # 3. Apply Scenario-Specific Physics Signatures
        if self.current_scenario == "lost_circulation":
            # Progression severity factor alpha: ramps from 0.0 to 1.0 during onset
            if self.scenario_phase == "onset":
                alpha = self.scenario_step / (self.max_scenario_steps * 0.20)
            elif self.scenario_phase == "full_development":
                alpha = 1.0
            else:  # stabilizing / recovery
                alpha = max(0.2, 1.0 - (self.scenario_step - self.max_scenario_steps * 0.75) / (self.max_scenario_steps * 0.25))

            # Severe drop in returns (Flow Out < Flow In)
            loss_flow_delta = -450.0 * alpha + float(np.random.normal(0, 25.0))
            flow_out = max(800.0, flow_in + loss_flow_delta)
            
            # Loss of annular hydrostatic head causes Standpipe Pressure drop (-150 to -350 psi)
            spp -= (280.0 * alpha + float(np.random.normal(0, 20.0)))
            
            # Pit volume depletes steadily (loss of mud)
            pit_loss_rate = 0.45 * alpha
            self.pit_volume = max(20.0, self.pit_volume - pit_loss_rate)
            
            # Minor ECD drop due to fluid column level drop in annulus
            ecd = max(self.mud_weight + 0.01, self.mud_weight + 0.03 - (0.02 * alpha))
            
            # ROP slight decrease as hydraulic cleaning deteriorates
            rop = max(3.0, rop - (2.5 * alpha))

        elif self.current_scenario == "gas_kick_influx":
            if self.scenario_phase == "onset":
                alpha = self.scenario_step / (self.max_scenario_steps * 0.20)
            elif self.scenario_phase == "full_development":
                alpha = 1.0
            else:
                alpha = max(0.3, 1.0 - (self.scenario_step - self.max_scenario_steps * 0.75) / (self.max_scenario_steps * 0.25))

            # Drilling break: ROP surges as underbalanced porous gas sand is entered
            rop += (8.0 * alpha + float(np.random.normal(0, 0.8)))
            
            # Returns increase significantly above pump rate (Flow Out > Flow In)
            influx_flow_delta = 280.0 * alpha + float(np.random.normal(0, 20.0))
            flow_out = flow_in + influx_flow_delta
            
            # Pit volume gains steadily
            pit_gain_rate = 0.35 * alpha
            self.pit_volume = min(180.0, self.pit_volume + pit_gain_rate)
            
            # Gas units in returns spike dramatically
            gas_units = 25.0 + (550.0 * alpha) + float(np.random.normal(0, 30.0))
            
            # Gas cut mud lowers annular fluid density (ECD drops)
            ecd = max(self.mud_weight - 0.04, self.mud_weight + 0.05 - (0.08 * alpha))
            
            # SPP drops slightly or fluctuates as gas bubbles expand up the annulus
            spp -= (70.0 * alpha + math.sin(self.step) * 25.0)

        elif self.current_scenario == "stuck_pipe_packoff":
            if self.scenario_phase == "onset":
                alpha = self.scenario_step / (self.max_scenario_steps * 0.20)
            elif self.scenario_phase == "full_development":
                alpha = 1.0
            else:
                alpha = max(0.25, 1.0 - (self.scenario_step - self.max_scenario_steps * 0.75) / (self.max_scenario_steps * 0.25))

            # Torque surges with extreme erratic fluctuations (stick-slip / packoff)
            torque_surge = 12.0 * alpha + math.sin(self.step / 2.0) * 4.5 + float(np.random.normal(0, 1.8))
            torque += torque_surge
            
            # RPM stalls or oscillates wildly as the string fights sticking
            rpm = max(20.0, rpm - (45.0 * alpha) + float(np.random.normal(0, 5.0)))
            
            # Annular pack-off restricts pump circulation: SPP spikes significantly
            spp_spike = 380.0 * alpha + float(np.random.normal(0, 35.0))
            spp += spp_spike
            
            # Overpull on hook load during attempts to free string
            hook_load += (28.0 * alpha + float(np.random.normal(0, 3.0)))
            
            # ROP drops toward zero as rotation stalls
            rop = max(0.8, rop - (7.5 * alpha))

        # Store calculated physical parameters
        self.rop = round(rop, 2)
        self.wob = round(wob, 1)
        self.rpm = round(rpm, 1)
        self.torque = round(torque, 2)
        self.spp = round(spp, 1)
        self.flow_in = round(flow_in, 1)
        self.flow_out = round(flow_out, 1)
        self.delta_flow = round(self.flow_out - self.flow_in, 1)
        self.ecd = round(ecd, 2)
        self.hook_load = round(hook_load, 1)
        self.gas_units = round(max(0.0, gas_units), 1)
        self.pit_volume = round(self.pit_volume, 2)

        # Teale's Mechanical Specific Energy (MSE) calculation in psi
        # Bit diameter assumed 8.5 in -> Area = pi/4 * 8.5^2 = 56.745 sq in
        bit_area = 56.745
        # WOB in k-lbs (wob tonnes * 2.20462), Torque in ft-lbs (kNm * 737.562)
        wob_klbs = self.wob * 2.20462
        torque_ftlbs = self.torque * 737.562
        rop_fph = max(0.5, self.rop * 3.28084)
        teale_mse = (wob_klbs * 1000.0 / bit_area) + (
            (120.0 * math.pi * self.rpm * torque_ftlbs) / (bit_area * rop_fph / 60.0)
        )
        teale_mse_psi = round(min(500000.0, max(5000.0, teale_mse)), 1)

        # 4. Construct Full Telemetry Packet with Provenance Metadata
        provenance = {
            "classification": "[B] Realistic Physics-Based Simulation",
            "generator": "NWIS ScenarioDrillingSimulator v2.0",
            "scenario": self.current_scenario,
            "scenario_phase": self.scenario_phase,
            "step": self.step,
            "scenario_step": self.scenario_step,
            "seed": self.seed,
            "physics_engine": "Bingham-Plastic Hydraulics & Teale Mechanical Models",
            "is_synthetic": True,
            "disclaimer": "Synthetic telemetry generated for SIH engineering demonstration; not live downhole sensor feed.",
        }

        return {
            "well_id": self.well_id,
            "depth": self.current_depth,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "formation_name": self.formation,
            "rop": self.rop,
            "wob": self.wob,
            "rpm": self.rpm,
            "torque": self.torque,
            "standpipe_pressure": self.spp,
            "flow_rate": self.flow_in,
            "flow_in": self.flow_in,
            "flow_out": self.flow_out,
            "delta_flow": self.delta_flow,
            "pit_volume": self.pit_volume,
            "gas_units": self.gas_units,
            "mud_weight": self.mud_weight,
            "ecd": self.ecd,
            "hook_load": self.hook_load,
            "teale_mse_psi": teale_mse_psi,
            "inclination": round(1.5 + (self.current_depth / 1500.0), 2),
            "azimuth": 48.0,
            "is_simulated": True,
            "is_demo_data": True,
            "provenance": provenance,
        }


# Global singleton simulator instance for application runtime
simulator_instance = DrillingStreamSimulator()
