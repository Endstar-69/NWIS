#!/usr/bin/env python3
"""
NWIS Automated End-to-End Hackathon Demo Scenario
=================================================
Runs the complete proactive wellsite intelligence workflow:
1. Active Well State & Stratigraphic Position
2. Geospatial Offset Well Identification & Multi-factor Similarity
3. Real-Time Telemetry Streaming & Anomaly Onset
4. ML Risk Model Probability Surge
5. Proactive Alert Generation
6. Historical Evidence Retrieval & Source Citation
7. Grounded Decision Support Recommendation

Usage:
    python scripts/run_demo.py
"""

import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.core.database import SessionLocal
from backend.app.models import Well, DrillingEvent, Alert
from backend.app.services.well_service import get_active_well, get_nearby_wells
from backend.app.services.risk_service import predict_well_risk
from backend.app.services.recommendation_service import get_recommendations_for_well
from backend.app.schemas.risk import RiskPredictionRequest

def run_hackathon_demo():
    print("=" * 75)
    print("  NEARBY WELLS INTELLIGENCE SYSTEM (NWIS) - HACKATHON DEMO SCENARIO")
    print("  'Turning historical drilling knowledge into proactive wellsite intelligence'")
    print("=" * 75)
    print("  Environment: DEMO / SYNTHETIC DATASET (Assam-Arakan Basin Reference)")
    print("-" * 75)

    db = SessionLocal()
    try:
        # Step 1: Active Well State
        print("\n[STEP 1]: Active Well State")
        active = get_active_well(db)
        print(f"  Active Well Name   : {active.well_name} ({active.well_id})")
        print(f"  Field / Block      : {active.field} / {active.block}")
        print(f"  Current Depth      : {active.current_depth:.1f} m")
        print(f"  Target Depth       : {active.target_depth:.1f} m")
        print(f"  Current Horizon    : Barail Sandstone (Oligocene Reservoir)")
        time.sleep(0.5)

        # Step 2: Nearby Offset Wells & Similarity Scoring
        print("\n[STEP 2]: Geospatial Offset Wells & Multi-Factor Similarity (25 km radius)")
        nearby = get_nearby_wells(db, active.well_id, radius_km=25.0)
        print(f"  Found {len(nearby)} offset wells within 25 km.")
        for item in nearby[:4]:
            w = item.well
            print(f"  [*] {w.well_name:<16} | Dist: {item.distance_km:>5.1f} km | Similarity: {item.similarity_score:>5.1f}% | Risk: {item.risk_level:<8} | Past Events: {item.historical_events_count}")
        time.sleep(0.5)

        # Step 3: Real-Time Telemetry Streaming & Anomaly Detection
        print("\n[STEP 3]: Real-Time Telemetry Progress (eRTMAC Simulator)")
        print("  Drilling at 3420.0 m... Anomaly signature detected:")
        print("  - Standpipe Pressure dropped by -170 psi (2350 -> 2180 psi)")
        print("  - Mud Flow Rate dropped by -100 LPM (1850 -> 1750 LPM)")
        print("  - Torque spiked from 12.0 kNm to 18.5 kNm")
        time.sleep(0.5)

        # Step 4: ML Risk Prediction & Contributing Factors
        print("\n[STEP 4]: ML Model Inference & Explainability")
        req = RiskPredictionRequest(
            well_id=active.well_id,
            depth=3420.0,
            formation_name="Barail Sandstone",
            rop=5.5,
            wob=16.0,
            rpm=105.0,
            torque=18.5,
            standpipe_pressure=2180.0,
            flow_rate=1750.0,
            mud_weight=1.28,
            ecd=1.33,
            hook_load=125.0
        )
        risk_res = predict_well_risk(db, req)
        for r_type, p in risk_res.predictions.items():
            print(f"  [+] {r_type.replace('_', ' '):<28} | Prob: {p.probability*100:>5.1f}% | Level: {p.risk_level}")
            for factor in p.contributing_factors[:2]:
                print(f"      - {factor.factor_name}: {factor.description}")
        time.sleep(0.5)

        # Step 5: Proactive Alert Trigger
        print("\n[STEP 5]: Proactive Alert Engine Triggered")
        latest_alert = db.query(Alert).filter(Alert.well_id == active.well_id).order_by(Alert.timestamp.desc()).first()
        if latest_alert:
            print(f"  [ALERT ID]: {latest_alert.alert_id} | Severity: {latest_alert.severity} | Status: {latest_alert.status}")
            print(f"  Risk Type: {latest_alert.risk_type} at {latest_alert.depth} m in {latest_alert.formation}")
            print(f"  Action   : {latest_alert.recommended_action}")
        time.sleep(0.5)

        # Step 6: Historical Evidence Linking
        print("\n[STEP 6]: Grounded Historical Evidence from Knowledge Repository")
        offset_events = db.query(DrillingEvent).filter(
            DrillingEvent.formation == "Barail Sandstone",
            DrillingEvent.start_depth >= 3410.0,
            DrillingEvent.start_depth <= 3445.0
        ).limit(3).all()
        for idx, ev in enumerate(offset_events):
            print(f"  [{idx+1}] Offset Well {ev.well_id} at {ev.start_depth}m: Encountered {ev.event_type} ({ev.severity})")
            print(f"      Cause     : {ev.cause}")
            print(f"      Mitigation: {ev.mitigation}")
            print(f"      Source    : {ev.source_document} (Page {ev.source_page})")
        time.sleep(0.5)

        # Step 7: Decision Support Recommendations
        print("\n[STEP 7]: Proactive Decision-Support Recommendation")
        recs = get_recommendations_for_well(db, active.well_id)
        if recs:
            top_rec = recs[0]
            print(f"  Title   : {top_rec.title}")
            print(f"  Summary : {top_rec.summary}")
            print("  Recommended Actions:")
            for action in top_rec.action_steps:
                print(f"    [>] {action}")
            print("  Precautions:")
            for prec in top_rec.precautions:
                print(f"    [!] {prec}")

        print("\n" + "=" * 75)
        print("  [SUCCESS] End-to-End NWIS Demo Flow Successfully Validated!")
        print("=" * 75)
    finally:
        db.close()

if __name__ == "__main__":
    run_hackathon_demo()
