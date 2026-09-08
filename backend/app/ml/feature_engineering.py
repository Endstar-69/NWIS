import numpy as np
import pandas as pd
from typing import Dict, List, Any

FORMATION_RISK_MAP = {
    "Alluvium": 0.10,
    "Dhekiajuli Sandstone": 0.20,
    "Girujan Clay": 0.55,
    "Tipam Sandstone": 0.65,
    "Bokabil Formation": 0.75,
    "Barail Sandstone": 0.85,
    "Barail Coal-Shale": 0.95,
    "Kopili Formation": 0.88,
    "Sylhet Limestone": 0.92,
    "Disang Formation": 0.80
}

FORMATION_PORE_PRESSURE_MAP = {
    "Alluvium": 1.00,
    "Dhekiajuli Sandstone": 1.02,
    "Girujan Clay": 1.05,
    "Tipam Sandstone": 1.08,
    "Bokabil Formation": 1.15,
    "Barail Sandstone": 1.28,
    "Barail Coal-Shale": 1.34,
    "Kopili Formation": 1.42,
    "Sylhet Limestone": 1.10,
    "Disang Formation": 1.38
}

FEATURE_COLUMNS = [
    "depth", "rop", "wob", "rpm", "torque", "standpipe_pressure", "flow_rate",
    "mud_weight", "ecd", "hook_load", "inclination", "azimuth",
    "torque_delta", "rop_delta", "pressure_delta", "flow_delta",
    "overbalance_sg", "mse", "formation_risk_score", "historical_event_density"
]

def calculate_mse(wob_tons: float, rop_mhr: float, rpm: float, torque_knm: float, hole_size_inch: float = 8.5) -> float:
    """
    Computes Teale's Mechanical Specific Energy (MSE) approximation in MPa.
    """
    hole_area_sq_inch = np.pi * (hole_size_inch / 2.0) ** 2
    safe_rop = max(0.5, rop_mhr)
    wob_lbs = wob_tons * 2204.62
    torque_ft_lbs = torque_knm * 737.562
    
    # MSE = (WOB / Area) + (120 * pi * RPM * Torque) / (Area * ROP_ft_hr)
    rop_ft_hr = safe_rop * 3.28084
    axial_comp = wob_lbs / hole_area_sq_inch
    rotational_comp = (120 * np.pi * max(10, rpm) * torque_ft_lbs) / (hole_area_sq_inch * rop_ft_hr)
    mse_psi = axial_comp + rotational_comp
    return round(float(mse_psi / 145.038), 2) # Return in MPa

def extract_features_from_dict(row: dict, historical_events: List[dict] = None) -> Dict[str, float]:
    """
    Extracts a normalized feature dictionary from a single telemetry point.
    """
    depth = float(row.get("depth", 0.0))
    rop = float(row.get("rop", 10.0))
    wob = float(row.get("wob", 12.0))
    rpm = float(row.get("rpm", 100.0))
    torque = float(row.get("torque", 10.0))
    spp = float(row.get("standpipe_pressure", 2200.0))
    flow = float(row.get("flow_rate", 1900.0))
    mw = float(row.get("mud_weight", 1.25))
    ecd = float(row.get("ecd", mw + 0.05))
    hkld = float(row.get("hook_load", 100.0))
    inc = float(row.get("inclination", 0.0))
    az = float(row.get("azimuth", 0.0))
    fmt = str(row.get("formation_name", "Barail Sandstone"))

    fmt_risk = FORMATION_RISK_MAP.get(fmt, 0.5)
    fmt_pp = FORMATION_PORE_PRESSURE_MAP.get(fmt, 1.15)
    overbalance = max(0.0, ecd - fmt_pp)

    # Historical event density: count events within +/- 150m of current depth
    # NOTE: This is populated ONLY from actual historical_events passed from the database.
    # Phase 0 fix: removed the hardcoded `event_density = 4` for the 3350-3500m Barail
    # window, which was scripting a fixed anomaly trigger rather than computing from data.
    event_density = 0
    if historical_events:
        for ev in historical_events:
            ev_d = float(ev.get("start_depth", 0.0))
            if abs(ev_d - depth) <= 150.0:
                event_density += 1

    # Simulated deltas for single point if rolling not provided
    torque_delta = float(row.get("torque_delta", max(0.0, torque - 12.0)))
    rop_delta = float(row.get("rop_delta", min(0.0, rop - 12.0)))
    pressure_delta = float(row.get("pressure_delta", spp - 2400.0))
    flow_delta = float(row.get("flow_delta", flow - 2000.0))
    mse = calculate_mse(wob, rop, rpm, torque)

    return {
        "depth": depth,
        "rop": rop,
        "wob": wob,
        "rpm": rpm,
        "torque": torque,
        "standpipe_pressure": spp,
        "flow_rate": flow,
        "mud_weight": mw,
        "ecd": ecd,
        "hook_load": hkld,
        "inclination": inc,
        "azimuth": az,
        "torque_delta": torque_delta,
        "rop_delta": rop_delta,
        "pressure_delta": pressure_delta,
        "flow_delta": flow_delta,
        "overbalance_sg": round(overbalance, 3),
        "mse": mse,
        "formation_risk_score": fmt_risk,
        "historical_event_density": float(event_density)
    }
