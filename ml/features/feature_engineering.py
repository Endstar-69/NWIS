"""
NWIS ML Feature Engineering Module.
Builds tabular drilling features, rolling telemetry deltas, and offset historical risk densities.
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np

def build_features_from_telemetry(data: Dict[str, Any], historical_events: List[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Constructs a 1-row feature DataFrame suitable for model inference.
    """
    depth = float(data.get("depth", 3420.0))
    formation = data.get("formation", "Barail Sandstone")
    
    # Calculate proximity to known historical problem zones
    event_density = 0
    min_dist_to_event = 9999.0
    if historical_events:
        for ev in historical_events:
            ev_depth = ev.get("start_depth", 0.0)
            dist = abs(depth - ev_depth)
            if dist < min_dist_to_event:
                min_dist_to_event = dist
            if dist <= 50.0:
                event_density += 1
    else:
        min_dist_to_event = 15.0
        event_density = 3

    features = {
        "depth": depth,
        "rop": float(data.get("rop", 15.0)),
        "wob": float(data.get("wob", 22.0)),
        "rpm": float(data.get("rpm", 110.0)),
        "torque": float(data.get("torque", 14.5)),
        "standpipe_pressure": float(data.get("standpipe_pressure", 2800.0)),
        "flow_rate": float(data.get("flow_rate", 550.0)),
        "mud_weight": float(data.get("mud_weight", 1.28)),
        "ecd": float(data.get("ecd", 1.34)),
        "hook_load": float(data.get("hook_load", 140.0)),
        "torque_delta": float(data.get("torque_delta", 1.2)),
        "rop_delta": float(data.get("rop_delta", -0.5)),
        "pressure_delta": float(data.get("pressure_delta", -40.0)),
        "rolling_torque": float(data.get("rolling_torque", 14.0)),
        "rolling_rop": float(data.get("rolling_rop", 15.2)),
        "rolling_pressure": float(data.get("rolling_pressure", 2840.0)),
        "historical_event_density": event_density,
        "dist_to_historical_event": min_dist_to_event
    }
    return pd.DataFrame([features])
