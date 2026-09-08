import asyncio
import json
from datetime import datetime, timezone
from backend.app.realtime.websocket_manager import ws_manager
from backend.app.core.database import SessionLocal
from backend.app.models.well import Well
from backend.app.schemas.risk import RiskPredictionRequest
from backend.app.services.risk_service import predict_well_risk
from simulator.drilling_stream import simulator_instance

simulation_running = False

async def start_telemetry_broadcast_loop():
    """
    Asynchronously ticks the simulator every 2 seconds and broadcasts
    live telemetry and realtime ML risk evaluations to connected WebSocket clients.
    """
    global simulation_running
    simulation_running = True
    print("[INFO] Real-time Telemetry Simulator Broadcast Loop initialized.")

    while simulation_running:
        try:
            # 1. Generate live telemetry tick
            telemetry = simulator_instance.tick()
            well_id = telemetry["well_id"]

            # 2. Run live ML risk prediction
            db = SessionLocal()
            try:
                # Update current depth in Well record for consistency
                well = db.query(Well).filter(Well.well_id == well_id).first()
                if well:
                    well.current_depth = telemetry["depth"]
                    db.commit()

                req = RiskPredictionRequest(
                    well_id=well_id,
                    depth=telemetry["depth"],
                    formation_name=telemetry["formation_name"],
                    rop=telemetry["rop"],
                    wob=telemetry["wob"],
                    rpm=telemetry["rpm"],
                    torque=telemetry["torque"],
                    standpipe_pressure=telemetry["standpipe_pressure"],
                    flow_rate=telemetry["flow_rate"],
                    mud_weight=telemetry["mud_weight"],
                    ecd=telemetry["ecd"],
                    hook_load=telemetry["hook_load"],
                    inclination=telemetry["inclination"],
                    azimuth=telemetry["azimuth"]
                )
                risk_res = predict_well_risk(db, req)
                risk_dict = risk_res.model_dump()
            finally:
                db.close()

            # 3. Form unified live payload
            payload = {
                "type": "TELEMETRY_UPDATE",
                "telemetry": telemetry,
                "risk_analysis": risk_dict,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            # 4. Broadcast to active well subscribers
            await ws_manager.broadcast_to_well(well_id, payload)
            # Also broadcast to "ALL" channel
            await ws_manager.broadcast_to_well("ALL", payload)

        except Exception as e:
            print(f"[ERROR] Telemetry broadcast loop error: {e}")

        await asyncio.sleep(2.0)
