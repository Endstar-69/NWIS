#!/usr/bin/env python3
"""
NWIS Demo Risk Inference CLI
============================
Quickly tests ML risk inference on realistic parameter inputs.

Usage:
    python scripts/predict_demo.py
"""

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.core.database import SessionLocal
from backend.app.schemas.risk import RiskPredictionRequest
from backend.app.services.risk_service import predict_well_risk

def run_prediction_demo():
    print("=" * 65)
    print(" NWIS ML Risk Prediction - Live Inference Demo")
    print("=" * 65)

    db = SessionLocal()
    try:
        # Sample anomalous parameter row representing Barail Sandstone depleted loss zone
        sample_request = RiskPredictionRequest(
            well_id="WELL-001",
            depth=3420.0,
            formation_name="Barail Sandstone",
            rop=5.2,
            wob=16.5,
            rpm=105.0,
            torque=18.5,
            standpipe_pressure=2180.0,
            flow_rate=1750.0,
            mud_weight=1.28,
            ecd=1.33,
            hook_load=122.0,
            inclination=1.8,
            azimuth=48.0
        )

        print("\n[INPUT TELEMETRY PARAMETERS]:")
        print(f"  Well ID          : {sample_request.well_id} (Dikom-104A)")
        print(f"  Current Depth    : {sample_request.depth} m")
        print(f"  Formation        : {sample_request.formation_name}")
        print(f"  ROP              : {sample_request.rop} m/hr")
        print(f"  Torque           : {sample_request.torque} kNm (Elevated)")
        print(f"  Standpipe Press  : {sample_request.standpipe_pressure} psi (Drop: -170 psi)")
        print(f"  Flow Rate        : {sample_request.flow_rate} LPM (Drop: -100 LPM)")

        result = predict_well_risk(db, sample_request)

        print("\n[ML RISK PREDICTION OUTPUT]:")
        print(f"  Overall Risk Level : {result.overall_risk_level}")

        for r_type, p in result.predictions.items():
            print(f"\n  • {r_type.replace('_', ' '):<28} | Prob: {p.probability*100:>5.1f}% | Level: {p.risk_level:<8}")
            for factor in p.contributing_factors:
                print(f"      - [{factor.impact_level}] {factor.factor_name}: {factor.description}")

        print(f"\n[HISTORICAL EVIDENCE]: Found {len(result.nearby_historical_evidence)} matching incidents in offset wells at this horizon.")
        for ev in result.nearby_historical_evidence[:2]:
            print(f"  - Well {ev['well_id']} at {ev['depth']}m ({ev['event_type']}): {ev['mitigation'][:80]}...")

        print("\n" + "=" * 65)
        print("[SUCCESS] Inference demo completed successfully!")
        print("=" * 65)
    finally:
        db.close()

if __name__ == "__main__":
    run_prediction_demo()
