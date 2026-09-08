#!/usr/bin/env python3
"""
NWIS Database Seeder
====================
Seeds the SQLite/PostgreSQL database with:
- Default Role-based Demo Users
- Synthetic Wells, Formations, Trajectories
- Drilling Parameters, Events, Casing, Cementing, Mud Programs
- Initial Proactive Alerts & Recommendations

Usage:
    python scripts/seed_database.py
"""

import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

# Add backend to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.core.database import engine, SessionLocal, Base
from backend.app.core.security import get_password_hash
from backend.app.models import (
    User, Well, WellTrajectory, Formation, DrillingParameter,
    DrillingEvent, Casing, Cementing, MudProgram, Alert, Recommendation, AuditLog
)

DEMO_DIR = BASE_DIR / "data" / "demo"

def seed_database():
    print("[INFO] Initializing NWIS Database schema...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Seed Demo Users
        print("[INFO] Seeding Demo Users...")
        default_users = [
            {
                "username": "driller",
                "email": "driller@oilindia.demo",
                "password": "password123",
                "full_name": "Rupen Bora (Drilling Lead)",
                "role": "Drilling Engineer"
            },
            {
                "username": "geologist",
                "email": "geologist@oilindia.demo",
                "password": "password123",
                "full_name": "Ananya Saikia (Sr. Geologist)",
                "role": "Geologist"
            },
            {
                "username": "supervisor",
                "email": "supervisor@oilindia.demo",
                "password": "password123",
                "full_name": "Debabrata Sarmah (Wellsite Supervisor)",
                "role": "Supervisor"
            },
            {
                "username": "admin",
                "email": "admin@oilindia.demo",
                "password": "adminpassword",
                "full_name": "System Administrator",
                "role": "Admin"
            },
            {
                "username": "viewer",
                "email": "viewer@oilindia.demo",
                "password": "password123",
                "full_name": "Executive Observer",
                "role": "Viewer"
            }
        ]
        
        for u in default_users:
            user_obj = db.query(User).filter(User.username == u["username"]).first()
            if not user_obj:
                user_obj = User(
                    username=u["username"],
                    email=u["email"],
                    hashed_password=get_password_hash(u["password"]),
                    full_name=u["full_name"],
                    role=u["role"],
                    is_active=True
                )
                db.add(user_obj)
            else:
                user_obj.hashed_password = get_password_hash(u["password"])
                user_obj.role = u["role"]
                user_obj.full_name = u["full_name"]
        db.commit()

        # 2. Seed Formations
        print("[INFO] Seeding Formations...")
        if (DEMO_DIR / "formations.csv").exists():
            df_fmt = pd.read_csv(DEMO_DIR / "formations.csv")
            for _, row in df_fmt.iterrows():
                if not db.query(Formation).filter(Formation.formation_id == row["formation_id"]).first():
                    db.add(Formation(
                        formation_id=row["formation_id"],
                        formation_name=row["formation_name"],
                        lithology=row["lithology"],
                        age_era=row["age_era"],
                        typical_top_depth=row["typical_top_depth"],
                        typical_bottom_depth=row["typical_bottom_depth"],
                        pore_pressure_gradient_sg=row["pore_pressure_gradient_sg"],
                        fracture_gradient_sg=row["fracture_gradient_sg"],
                        known_hazards=row["known_hazards"],
                        drillability_rating=row["drillability_rating"],
                        risk_level=row["risk_level"],
                        color_hex=row["color_hex"],
                        is_demo_data=True
                    ))
            db.commit()

        # 3. Seed Wells
        print("[INFO] Seeding Wells...")
        if (DEMO_DIR / "wells.csv").exists():
            df_wells = pd.read_csv(DEMO_DIR / "wells.csv")
            for _, row in df_wells.iterrows():
                existing = db.query(Well).filter(Well.well_id == row["well_id"]).first()
                if not existing:
                    db.add(Well(
                        well_id=row["well_id"],
                        well_name=row["well_name"],
                        field=row["field"],
                        block=row["block"],
                        basin=row["basin"],
                        operator=row["operator"],
                        well_type=row["well_type"],
                        status=row["status"],
                        target_depth=row["target_depth"],
                        current_depth=row["current_depth"],
                        latitude=row["latitude"],
                        longitude=row["longitude"],
                        spud_date=str(row["spud_date"]),
                        completion_date=str(row["completion_date"]) if pd.notna(row["completion_date"]) else None,
                        is_active_well=bool(row["is_active_well"]),
                        is_demo_data=True,
                        data_source=row["data_source"]
                    ))
            db.commit()

        # 4. Seed Trajectories
        print("[INFO] Seeding Well Trajectories...")
        if (DEMO_DIR / "trajectories.csv").exists():
            df_traj = pd.read_csv(DEMO_DIR / "trajectories.csv")
            if db.query(WellTrajectory).count() == 0:
                traj_objs = [
                    WellTrajectory(
                        well_id=row["well_id"],
                        measured_depth=row["measured_depth"],
                        true_vertical_depth=row["true_vertical_depth"],
                        inclination=row["inclination"],
                        azimuth=row["azimuth"],
                        dogleg_severity=row["dogleg_severity"],
                        easting=row["easting"],
                        northing=row["northing"]
                    )
                    for _, row in df_traj.iterrows()
                ]
                db.bulk_save_objects(traj_objs)
                db.commit()

        # 5. Seed Historical Events
        print("[INFO] Seeding Drilling Historical Events...")
        if (DEMO_DIR / "drilling_events.csv").exists():
            df_evt = pd.read_csv(DEMO_DIR / "drilling_events.csv")
            if db.query(DrillingEvent).count() == 0:
                evt_objs = [
                    DrillingEvent(
                        event_id=row["event_id"],
                        well_id=row["well_id"],
                        event_type=row["event_type"],
                        start_depth=row["start_depth"],
                        end_depth=row["end_depth"],
                        formation=row["formation"],
                        severity=row["severity"],
                        cause=row["cause"],
                        impact=row["impact"],
                        mitigation=row["mitigation"],
                        lesson_learned=row["lesson_learned"],
                        npt_hours=row["npt_hours"],
                        source_document=row["source_document"],
                        source_page=int(row["source_page"]),
                        confidence=row["confidence"],
                        is_demo_data=True
                    )
                    for _, row in df_evt.iterrows()
                ]
                db.bulk_save_objects(evt_objs)
                db.commit()

        # 6. Seed Drilling Parameters
        print("[INFO] Seeding Drilling Telemetry Parameters...")
        if (DEMO_DIR / "drilling_parameters.csv").exists():
            df_param = pd.read_csv(DEMO_DIR / "drilling_parameters.csv")
            if db.query(DrillingParameter).count() == 0:
                param_objs = [
                    DrillingParameter(
                        well_id=row["well_id"],
                        depth=row["depth"],
                        rop=row["rop"],
                        wob=row["wob"],
                        rpm=row["rpm"],
                        torque=row["torque"],
                        standpipe_pressure=row["standpipe_pressure"],
                        flow_rate=row["flow_rate"],
                        mud_weight=row["mud_weight"],
                        ecd=row["ecd"],
                        hook_load=row["hook_load"],
                        inclination=row["inclination"],
                        azimuth=row["azimuth"],
                        formation_name=row["formation_name"],
                        hole_size=row["hole_size"],
                        bit_type=row["bit_type"],
                        is_simulated=bool(row["is_simulated"]),
                        is_demo_data=True
                    )
                    for _, row in df_param.iterrows()
                ]
                db.bulk_save_objects(param_objs)
                db.commit()

        # 7. Seed Casing, Cementing, Mud Programs
        print("[INFO] Seeding Casing, Cementing & Mud Programs...")
        if (DEMO_DIR / "casing.csv").exists() and db.query(Casing).count() == 0:
            df_c = pd.read_csv(DEMO_DIR / "casing.csv")
            db.bulk_save_objects([Casing(**row.to_dict()) for _, row in df_c.iterrows()])
            db.commit()

        if (DEMO_DIR / "cementing.csv").exists() and db.query(Cementing).count() == 0:
            df_cm = pd.read_csv(DEMO_DIR / "cementing.csv")
            db.bulk_save_objects([Cementing(**row.to_dict()) for _, row in df_cm.iterrows()])
            db.commit()

        if (DEMO_DIR / "mud_programs.csv").exists() and db.query(MudProgram).count() == 0:
            df_mp = pd.read_csv(DEMO_DIR / "mud_programs.csv")
            db.bulk_save_objects([MudProgram(**row.to_dict()) for _, row in df_mp.iterrows()])
            db.commit()

        # 8. Seed Initial Proactive Alerts
        print("[INFO] Seeding Initial Proactive Alerts...")
        if db.query(Alert).count() == 0:
            initial_alerts = [
                Alert(
                    alert_id="ALT-001",
                    well_id="WELL-001",
                    timestamp=datetime.now(timezone.utc),
                    depth=3420.0,
                    formation="Barail Sandstone",
                    risk_type="MUD_LOSS",
                    severity="HIGH",
                    probability=0.78,
                    reasons_json='["Current depth (3420 m) overlaps known depleted reservoir loss zone", "Historical loss density is 75% in nearby offset wells at this horizon", "Standpipe pressure delta dropped -150 psi in last 10 metres", "Flow out paddle shows slight loss deviation"]',
                    historical_evidence_json='[{"well_name": "Dikom-14", "distance_km": 1.4, "depth": 3418.0, "event": "MUD_LOSS", "mitigation": "Pumped 35 bbl high-fluid-loss LCM pill and reduced mud weight from 1.32 to 1.26 SG"}, {"well_name": "Dikom-22", "distance_km": 2.1, "depth": 3434.0, "event": "MUD_LOSS", "mitigation": "Reduced pump rate to 1800 LPM and spotted CaCO3 bridging pill"}]',
                    recommended_action="Prepare LCM pill (CaCO3 medium/coarse) on surface pit; reduce pump rate to 1850 LPM; adjust mud weight toward lower operating window (1.26 SG) under supervisor review.",
                    status="NEW",
                    is_demo_data=True
                ),
                Alert(
                    alert_id="ALT-002",
                    well_id="WELL-001",
                    timestamp=datetime.now(timezone.utc),
                    depth=3420.0,
                    formation="Barail Sandstone",
                    risk_type="STUCK_PIPE",
                    severity="WATCH",
                    probability=0.43,
                    reasons_json='["Elevated torque fluctuations (+3.5 kNm) detected", "Static time > 2.5 minutes while surveying in permeable zone", "Overbalance pressure estimated at ~380 psi"]',
                    historical_evidence_json='[{"well_name": "Dikom-18", "distance_km": 1.9, "depth": 3422.0, "event": "STUCK_PIPE", "mitigation": "Jarred downward with 40 bbl lubricating oil pill for 4 hours"}]',
                    recommended_action="Maintain continuous drillstring rotation and reciprocation; avoid stationary surveys exceeding 3 minutes across Barail Sand horizon.",
                    status="NEW",
                    is_demo_data=True
                )
            ]
            for a in initial_alerts:
                db.add(a)
            db.commit()

        # Audit Log
        db.add(AuditLog(
            username="system",
            action="DATABASE_SEED",
            resource_type="DATABASE",
            resource_id="ALL",
            details_json='{"status": "SUCCESS", "mode": "DEMO_SYNTHETIC"}'
        ))
        db.commit()

        print("[SUCCESS] Database successfully seeded with demo dataset!")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
