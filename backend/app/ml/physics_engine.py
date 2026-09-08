"""
NWIS Deterministic Engineering Physics Engine — Phase 3 Implementation.

CLASSIFICATION: [A] Real Implementation (Tier 1 Physics Engine).
Calculates deterministic drilling mechanics and wellbore hydraulics with zero hardcoded depth triggers.

Engineering Physics Principles:
  1. Teale's Mechanical Specific Energy (MSE):
     MSE = (WOB / A_bit) + (120 * pi * RPM * Torque) / (A_bit * ROP)
  2. Wellbore Hydraulic Balance:
     - Formation pore pressure gradient (PP)
     - Formation fracture gradient (FG)
     - Overbalance margin: ECD - PP
     - Fracture margin: FG - ECD
  3. Pressure & Flow Balance Deltas:
     - Negative flow delta (Flow Out < Flow In) + negative SPP delta -> Lost Circulation
     - Positive flow delta (Flow Out > Flow In) + narrow overbalance -> Kick / Influx
     - High torque + high overbalance + elevated MSE -> Differential / Mechanical Sticking
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from backend.app.schemas.risk import RiskFactorDetail

# Stratigraphic pore pressure gradient mapping (SG)
FORMATION_PORE_PRESSURE_MAP: Dict[str, float] = {
    "Alluvium": 1.00,
    "Dhekiajuli Sandstone": 1.02,
    "Girujan Clay": 1.05,
    "Tipam Sandstone": 1.08,
    "Bokabil Formation": 1.15,
    "Barail Sandstone": 1.28,
    "Barail Coal-Shale": 1.34,
    "Kopili Formation": 1.42,
    "Sylhet Limestone": 1.10,
    "Disang Formation": 1.38,
}

# Formation unconfined compressive rock strength (UCS in MPa) for MSE baseline
FORMATION_UCS_MAP: Dict[str, float] = {
    "Alluvium": 8.0,
    "Dhekiajuli Sandstone": 18.0,
    "Girujan Clay": 25.0,
    "Tipam Sandstone": 35.0,
    "Bokabil Formation": 42.0,
    "Barail Sandstone": 55.0,
    "Barail Coal-Shale": 48.0,
    "Kopili Formation": 65.0,
    "Sylhet Limestone": 75.0,
    "Disang Formation": 70.0,
}

# Formation permeability / loss tendency factor (0.0 to 1.0)
FORMATION_LOSS_TENDENCY_MAP: Dict[str, float] = {
    "Alluvium": 0.20,
    "Dhekiajuli Sandstone": 0.35,
    "Girujan Clay": 0.15,
    "Tipam Sandstone": 0.50,
    "Bokabil Formation": 0.40,
    "Barail Sandstone": 0.85,
    "Barail Coal-Shale": 0.30,
    "Kopili Formation": 0.25,
    "Sylhet Limestone": 0.90,
    "Disang Formation": 0.30,
}


def calculate_teale_mse(
    wob_tons: float,
    rop_mhr: float,
    rpm: float,
    torque_knm: float,
    hole_size_inch: float = 8.5,
) -> Dict[str, float]:
    """
    Computes Teale's Mechanical Specific Energy (MSE).
    
    Formula:
        MSE = (WOB / A_bit) + (120 * pi * RPM * Torque) / (A_bit * ROP)
        
    Returns:
        Dict with:
          - mse_mpa: MSE in Megapascals (SI)
          - mse_psi: MSE in psi (oilfield)
          - axial_ratio: fraction of energy from WOB
          - rotational_ratio: fraction of energy from rotary torque
    """
    safe_rop_mhr = max(0.2, float(rop_mhr))
    safe_wob = max(1.0, float(wob_tons))
    safe_rpm = max(10.0, float(rpm))
    safe_torque = max(0.5, float(torque_knm))

    hole_area_sq_in = (math.pi / 4.0) * (hole_size_inch ** 2)

    # Convert to oilfield units: WOB in lbs, Torque in ft-lbs, ROP in ft/hr
    wob_lbs = safe_wob * 2204.62
    torque_ft_lbs = safe_torque * 737.562
    rop_ft_hr = safe_rop_mhr * 3.28084

    # Axial and rotational components in psi
    axial_comp_psi = wob_lbs / hole_area_sq_in
    rotational_comp_psi = (120.0 * math.pi * safe_rpm * torque_ft_lbs) / (hole_area_sq_in * (rop_ft_hr / 60.0) * 60.0)
    total_mse_psi = axial_comp_psi + rotational_comp_psi

    # Convert to MPa (1 psi = 0.00689476 MPa)
    mse_mpa = total_mse_psi * 0.00689476
    bounded_mse_mpa = round(float(np.clip(mse_mpa, 5.0, 1500.0)), 2)
    bounded_mse_psi = round(float(np.clip(total_mse_psi, 700.0, 220000.0)), 1)

    total_safe = max(1.0, total_mse_psi)
    return {
        "mse_mpa": bounded_mse_mpa,
        "mse_psi": bounded_mse_psi,
        "axial_ratio": round(axial_comp_psi / total_safe, 3),
        "rotational_ratio": round(rotational_comp_psi / total_safe, 3),
    }


def calculate_hydraulic_balance(
    depth: float,
    mud_weight: float,
    ecd: float,
    formation_name: str,
) -> Dict[str, float]:
    """
    Computes formation pore pressure, fracture gradient, and circulating hydraulic margins.
    
    Returns:
        Dict with pore_pressure_sg, fracture_gradient_sg, overbalance_margin_sg,
        fracture_margin_sg, and bottom_hole_pressure_bar.
    """
    safe_depth = max(100.0, float(depth))
    safe_ecd = max(1.0, float(ecd))
    safe_mw = max(1.0, float(mud_weight))

    pore_pressure_sg = FORMATION_PORE_PRESSURE_MAP.get(formation_name, 1.15)
    
    # Empirical fracture gradient estimation based on Hubbert-Willis / Eaton correlation:
    # FG increases with depth and pore pressure
    depth_comp = (safe_depth / 10000.0) * 0.06
    fracture_gradient_sg = round(pore_pressure_sg + 0.18 + depth_comp, 3)

    # Margins in SG
    overbalance_margin_sg = round(safe_ecd - pore_pressure_sg, 3)
    fracture_margin_sg = round(fracture_gradient_sg - safe_ecd, 3)

    # Hydrostatic & circulating bottom hole pressure in bar
    # P (bar) = 0.0981 * rho (sg) * depth (m)
    bhp_bar = round(0.0981 * safe_ecd * safe_depth, 1)

    return {
        "pore_pressure_sg": pore_pressure_sg,
        "fracture_gradient_sg": fracture_gradient_sg,
        "overbalance_margin_sg": overbalance_margin_sg,
        "fracture_margin_sg": fracture_margin_sg,
        "bhp_bar": bhp_bar,
    }


def _safe_float(val: Any, default: float) -> float:
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def evaluate_tier1_physics_risk(
    telemetry: Dict[str, Any],
    historical_events: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[Dict[str, float], Dict[str, Any], Dict[str, List[RiskFactorDetail]]]:
    """
    Tier 1 Deterministic Physics-Informed Risk Engine.
    
    Returns:
      1. physics_scores: { "MUD_LOSS": float, "STUCK_PIPE": float, "KICK": float }
      2. physics_metrics: calculated engineering parameters (MSE, overbalance, FG, deltas)
      3. factor_warnings: physics-grounded explanations per risk type
    """
    depth = _safe_float(telemetry.get("depth"), 3400.0)
    rop = _safe_float(telemetry.get("rop"), 9.5)
    wob = _safe_float(telemetry.get("wob"), 15.0)
    rpm = _safe_float(telemetry.get("rpm"), 110.0)
    torque = _safe_float(telemetry.get("torque"), 13.0)
    spp = _safe_float(telemetry.get("standpipe_pressure"), 2350.0)
    flow_in = _safe_float(telemetry.get("flow_in"), _safe_float(telemetry.get("flow_rate"), 1950.0))
    flow_out = _safe_float(telemetry.get("flow_out"), flow_in)
    delta_flow = _safe_float(telemetry.get("delta_flow"), flow_out - flow_in)
    mud_weight = _safe_float(telemetry.get("mud_weight"), 1.28)
    ecd = _safe_float(telemetry.get("ecd"), mud_weight + 0.05)
    formation_name = str(telemetry.get("formation_name") or "Barail Sandstone")
    gas_units = _safe_float(telemetry.get("gas_units"), 25.0)

    # 1. Teale's MSE
    mse_data = calculate_teale_mse(wob, rop, rpm, torque)
    mse_mpa = mse_data["mse_mpa"]
    ucs_baseline = FORMATION_UCS_MAP.get(formation_name, 45.0)
    mse_flounder_ratio = round(mse_mpa / max(10.0, ucs_baseline), 2)

    # 2. Hydraulic Balance
    hydraulics = calculate_hydraulic_balance(depth, mud_weight, ecd, formation_name)
    ob_margin = hydraulics["overbalance_margin_sg"]
    frac_margin = hydraulics["fracture_margin_sg"]

    # 3. Deltas from nominal drilling envelope
    nominal_spp = 2350.0 + (depth / 1000.0) * 25.0
    nominal_torque = 13.0 + (depth / 1000.0) * 0.85
    spp_delta = spp - nominal_spp
    torque_delta = torque - nominal_torque

    # 4. Historical event density in depth interval (+/- 120m)
    loss_events_nearby = 0
    stuck_events_nearby = 0
    kick_events_nearby = 0
    if historical_events:
        for ev in historical_events:
            ev_depth = float(ev.get("depth", ev.get("start_depth", 0.0)))
            if abs(ev_depth - depth) <= 120.0:
                ev_type = str(ev.get("event_type", "")).upper()
                if "LOSS" in ev_type or "MUD" in ev_type:
                    loss_events_nearby += 1
                elif "STUCK" in ev_type or "PACK" in ev_type:
                    stuck_events_nearby += 1
                elif "KICK" in ev_type or "CONTROL" in ev_type or "INFLUX" in ev_type:
                    kick_events_nearby += 1

    loss_tendency = FORMATION_LOSS_TENDENCY_MAP.get(formation_name, 0.4)

    # ── MUD LOSS PHYSICS EVALUATION ──────────────────────────────────────────
    mud_loss_score = 0.10
    mud_loss_factors: List[RiskFactorDetail] = []

    # Hydraulic fracture margin constraint
    if frac_margin < 0.02:  # ECD approaching or exceeding fracture gradient
        mud_loss_score += 0.45
        mud_loss_factors.append(RiskFactorDetail(
            factor_name="Fracture Gradient Margin Depletion",
            impact_level="HIGH",
            description=f"ECD ({ecd:.2f} SG) approaches formation fracture gradient ({hydraulics['fracture_gradient_sg']:.2f} SG). Fracture margin is only {frac_margin:.3f} SG.",
            contribution_score=0.45
        ))
    elif frac_margin < 0.06:
        mud_loss_score += 0.20
        mud_loss_factors.append(RiskFactorDetail(
            factor_name="Narrow Fracture Window",
            impact_level="MEDIUM",
            description=f"Operating with tight fracture window ({frac_margin:.3f} SG buffer to formation breakdown).",
            contribution_score=0.20
        ))

    # Annular return flow deficit
    if delta_flow < -100.0:
        mud_loss_score += 0.40
        mud_loss_factors.append(RiskFactorDetail(
            factor_name="Severe Annular Flow-Out Deficit",
            impact_level="HIGH",
            description=f"Returns deficit of {delta_flow:.1f} LPM (Flow In: {flow_in:.0f} vs Flow Out: {flow_out:.0f} LPM) indicates active fluid loss into thief zone.",
            contribution_score=0.40
        ))
    elif delta_flow < -35.0:
        mud_loss_score += 0.20
        mud_loss_factors.append(RiskFactorDetail(
            factor_name="Mild Return Flow Reduction",
            impact_level="MEDIUM",
            description=f"Flow deficit of {delta_flow:.1f} LPM suggests seepage or partial thief zone ingress.",
            contribution_score=0.20
        ))

    # Hydrostatic loss SPP drop
    if spp_delta < -80.0:
        mud_loss_score += 0.25
        mud_loss_factors.append(RiskFactorDetail(
            factor_name="Standpipe Pressure Loss Signature",
            impact_level="HIGH",
            description=f"Standpipe pressure dropped by {spp_delta:.1f} psi below hydrostatic baseline ({nominal_spp:.0f} psi).",
            contribution_score=0.25
        ))

    # Stratigraphic permeability and offset events
    if loss_tendency >= 0.80 and loss_events_nearby >= 1:
        mud_loss_score += 0.15
        mud_loss_factors.append(RiskFactorDetail(
            factor_name="High-Permeability Horizon with Offset Loss History",
            impact_level="MEDIUM",
            description=f"{formation_name} exhibits high fracture susceptibility with {loss_events_nearby} recorded offset loss events within +/-120m.",
            contribution_score=0.15
        ))

    mud_loss_prob = round(float(np.clip(mud_loss_score, 0.05, 0.98)), 2)

    # ── STUCK PIPE PHYSICS EVALUATION ────────────────────────────────────────
    stuck_pipe_score = 0.08
    stuck_pipe_factors: List[RiskFactorDetail] = []

    # Rotary torque surge
    if torque_delta > 6.0 or torque > 22.0:
        stuck_pipe_score += 0.45
        stuck_pipe_factors.append(RiskFactorDetail(
            factor_name="Critical Rotary Torque Surge",
            impact_level="HIGH",
            description=f"Torque spiked to {torque:.1f} kNm (+{torque_delta:.1f} kNm above baseline), signaling severe hole drag or cuttings pack-off.",
            contribution_score=0.45
        ))
    elif torque_delta > 2.5:
        stuck_pipe_score += 0.25
        stuck_pipe_factors.append(RiskFactorDetail(
            factor_name="Elevated Rotary Torque Drag",
            impact_level="MEDIUM",
            description=f"Rotary torque elevated (+{torque_delta:.1f} kNm), indicating increasing wellbore friction.",
            contribution_score=0.25
        ))

    # High overbalance differential sticking
    if ob_margin > 0.16:
        stuck_pipe_score += 0.35
        stuck_pipe_factors.append(RiskFactorDetail(
            factor_name="Excessive Overbalance Margin",
            impact_level="HIGH",
            description=f"Overbalance is {ob_margin:.3f} SG (~{int(ob_margin * 1420)} psi differential), creating severe differential sticking conditions against permeable filter cake.",
            contribution_score=0.35
        ))
    elif ob_margin > 0.12:
        stuck_pipe_score += 0.15
        stuck_pipe_factors.append(RiskFactorDetail(
            factor_name="Elevated Differential Pressure",
            impact_level="MEDIUM",
            description=f"Overbalance differential pressure ({ob_margin:.3f} SG) favors mud cake embedding.",
            contribution_score=0.15
        ))

    # Teale MSE floundering / bit balling
    if mse_flounder_ratio > 3.0:
        stuck_pipe_score += 0.25
        stuck_pipe_factors.append(RiskFactorDetail(
            factor_name="Extreme Teale MSE Floundering",
            impact_level="HIGH",
            description=f"Mechanical Specific Energy ({mse_mpa:.1f} MPa) is {mse_flounder_ratio:.1f}x rock UCS ({ucs_baseline:.0f} MPa), indicating severe bit floundering, vibration, or annular choke.",
            contribution_score=0.25
        ))
    elif mse_flounder_ratio > 1.8:
        stuck_pipe_score += 0.15
        stuck_pipe_factors.append(RiskFactorDetail(
            factor_name="Elevated Mechanical Specific Energy",
            impact_level="MEDIUM",
            description=f"Teale MSE ({mse_mpa:.1f} MPa) exceeds rock strength ({ucs_baseline:.0f} MPa), indicating suboptimal cutting efficiency.",
            contribution_score=0.15
        ))

    # Annular pack-off SPP escalation
    if spp_delta > 120.0:
        stuck_pipe_score += 0.20
        stuck_pipe_factors.append(RiskFactorDetail(
            factor_name="Circulation Pressure Pack-Off Escalation",
            impact_level="HIGH",
            description=f"Standpipe pressure increased by +{spp_delta:.1f} psi due to cuttings restriction in the annulus.",
            contribution_score=0.20
        ))

    stuck_pipe_prob = round(float(np.clip(stuck_pipe_score, 0.05, 0.98)), 2)

    # ── KICK / INFLUX PHYSICS EVALUATION ─────────────────────────────────────
    kick_score = 0.06
    kick_factors: List[RiskFactorDetail] = []

    # Underbalance / near-balance margin
    if ob_margin <= 0.01:
        kick_score += 0.50
        kick_factors.append(RiskFactorDetail(
            factor_name="Critical Wellbore Underbalance",
            impact_level="HIGH",
            description=f"Effective circulating density ({ecd:.2f} SG) is underbalanced or at threshold against formation pore pressure ({hydraulics['pore_pressure_sg']:.2f} SG, margin: {ob_margin:.3f} SG).",
            contribution_score=0.50
        ))
    elif ob_margin < 0.04:
        kick_score += 0.25
        kick_factors.append(RiskFactorDetail(
            factor_name="Narrow Overbalance Barrier",
            impact_level="MEDIUM",
            description=f"Overbalance buffer is dangerously narrow ({ob_margin:.3f} SG) across {formation_name}.",
            contribution_score=0.25
        ))

    # Flow out gain
    if delta_flow > 80.0:
        kick_score += 0.45
        kick_factors.append(RiskFactorDetail(
            factor_name="Active Annular Flow Influx",
            impact_level="HIGH",
            description=f"Flow Out exceeds Flow In by +{delta_flow:.1f} LPM, confirming positive wellbore influx.",
            contribution_score=0.45
        ))
    elif delta_flow > 30.0:
        kick_score += 0.20
        kick_factors.append(RiskFactorDetail(
            factor_name="Positive Delta-Flow Return",
            impact_level="MEDIUM",
            description=f"Return flow rate delta is positive (+{delta_flow:.1f} LPM), indicating potential formation fluid expansion.",
            contribution_score=0.20
        ))

    # Mud gas units surge
    if gas_units > 150.0:
        kick_score += 0.35
        kick_factors.append(RiskFactorDetail(
            factor_name="Severe Mud Gas Influx Spike",
            impact_level="HIGH",
            description=f"Return mud gas concentration spiked to {gas_units:.1f} units (baseline 25 units).",
            contribution_score=0.35
        ))
    elif gas_units > 60.0:
        kick_score += 0.15
        kick_factors.append(RiskFactorDetail(
            factor_name="Elevated Mud Gas Units",
            impact_level="MEDIUM",
            description=f"Gas in mud increased to {gas_units:.1f} units.",
            contribution_score=0.15
        ))

    # Drilling break in porous gas sand
    if rop > 16.0 and ob_margin < 0.06:
        kick_score += 0.20
        kick_factors.append(RiskFactorDetail(
            factor_name="Drilling Break in Underbalanced Horizon",
            impact_level="MEDIUM",
            description=f"Sudden ROP surge ({rop:.1f} m/hr) into underpressured/permeable porous sand.",
            contribution_score=0.20
        ))

    kick_prob = round(float(np.clip(kick_score, 0.05, 0.98)), 2)

    # Fallbacks if no warning factors triggered
    default_normal_factor = RiskFactorDetail(
        factor_name="Hydraulically Balanced Normal Baseline",
        impact_level="LOW",
        description="Physical parameters within acceptable operational tolerance window.",
        contribution_score=0.08
    )
    if not mud_loss_factors:
        mud_loss_factors.append(default_normal_factor)
    if not stuck_pipe_factors:
        stuck_pipe_factors.append(default_normal_factor)
    if not kick_factors:
        kick_factors.append(default_normal_factor)

    physics_scores = {
        "MUD_LOSS": mud_loss_prob,
        "STUCK_PIPE": stuck_pipe_prob,
        "KICK": kick_prob,
    }

    physics_metrics = {
        "teale_mse_mpa": mse_mpa,
        "teale_mse_psi": mse_data["mse_psi"],
        "mse_flounder_ratio": mse_flounder_ratio,
        "pore_pressure_sg": hydraulics["pore_pressure_sg"],
        "fracture_gradient_sg": hydraulics["fracture_gradient_sg"],
        "overbalance_margin_sg": ob_margin,
        "fracture_margin_sg": frac_margin,
        "bhp_bar": hydraulics["bhp_bar"],
        "delta_flow_lpm": delta_flow,
        "spp_delta_psi": round(spp_delta, 1),
        "torque_delta_knm": round(torque_delta, 2),
    }

    factor_warnings = {
        "MUD_LOSS": mud_loss_factors,
        "STUCK_PIPE": stuck_pipe_factors,
        "KICK": kick_factors,
    }

    return physics_scores, physics_metrics, factor_warnings
