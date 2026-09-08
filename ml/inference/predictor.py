"""
NWIS ML Inference Engine.
Loads saved models and runs real-time risk predictions with explainability explanations.
"""
from typing import Dict, Any
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.ml.inference import inference_engine

def predict_risks(telemetry_data: Dict[str, Any], historical_events: list = None) -> Dict[str, Any]:
    """
    Evaluates Mud Loss, Stuck Pipe, and Kick risk probabilities with explainable factors.
    """
    preds = inference_engine.predict_risk(telemetry_data, historical_events)
    return {k: v.model_dump() for k, v in preds.items()}

if __name__ == "__main__":
    sample_data = {
        "depth": 3422.0,
        "formation": "Barail Sandstone",
        "rop": 18.5,
        "wob": 24.0,
        "rpm": 115.0,
        "torque": 15.2,
        "standpipe_pressure": 2720.0,
        "flow_rate": 510.0,
        "mud_weight": 1.28,
        "ecd": 1.34,
        "hook_load": 142.0,
        "torque_delta": 1.5,
        "rop_delta": 1.2,
        "pressure_delta": -80.0,
        "rolling_torque": 14.8,
        "rolling_rop": 17.5,
        "rolling_pressure": 2800.0
    }
    print("[INFO] Running demo ML prediction...")
    results = predict_risks(sample_data)
    for model_name, res in results.items():
        print(f"\n{model_name} RISK: {res['risk_level']} ({res['probability']*100:.1f}%)")
        print("  Reasons:")
        for r in res.get("contributing_factors", []):
            print(f"    - {r.get('factor')}: {r.get('description')}")
