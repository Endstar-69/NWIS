import os
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import init_db, get_db
from backend.app.models import Well, Formation, DrillingEvent, Document, Alert, User
from backend.app.api import (
    auth_router, wells_router, formations_router, events_router,
    documents_router, search_router, risk_router, alerts_router,
    recommendations_router, analytics_router, simulator_router
)
from backend.app.realtime.websocket_manager import ws_manager
from backend.app.realtime.stream_handler import start_telemetry_broadcast_loop
from backend.app.ml.inference import inference_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    init_db()
    inference_engine.load_models()
    
    # Start background real-time simulator task
    sim_task = asyncio.create_task(start_telemetry_broadcast_loop())
    print(f"[INFO] {settings.APP_NAME} Backend Started (Environment: {settings.APP_ENV})")
    
    yield
    
    # Cleanup
    sim_task.cancel()
    print(f"[INFO] {settings.APP_NAME} Backend Shutdown")

app = FastAPI(
    title=settings.APP_NAME,
    description="Nearby Wells Intelligence System (NWIS) - AI/ML-enabled decision-support platform with institutional memory from offset wells for OIL India Limited.",
    version="1.0.0-prototype",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://nwis-oil.netlify.app",
        "https://nwis.vercel.app",
    ],
    allow_origin_regex=r"https://.*(\.netlify\.app|\.vercel\.app)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST Routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(wells_router, prefix=settings.API_PREFIX)
app.include_router(formations_router, prefix=settings.API_PREFIX)
app.include_router(events_router, prefix=settings.API_PREFIX)
app.include_router(documents_router, prefix=settings.API_PREFIX)
app.include_router(search_router, prefix=settings.API_PREFIX)
app.include_router(risk_router, prefix=settings.API_PREFIX)
app.include_router(alerts_router, prefix=settings.API_PREFIX)
app.include_router(recommendations_router, prefix=settings.API_PREFIX)
app.include_router(analytics_router, prefix=settings.API_PREFIX)
app.include_router(simulator_router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {
        "system": settings.APP_NAME,
        "status": "OPERATIONAL",
        "environment": "DEMO / SYNTHETIC DATA ENVIRONMENT",
        "api_docs": "/docs",
        "version": "1.0.0-prototype"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "system": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "1.0.0-prototype"
    }

@app.get("/api/system/status")
def get_system_status(db: Session = Depends(get_db)):
    wells_count = db.query(Well).count()
    events_count = db.query(DrillingEvent).count()
    docs_count = db.query(Document).count()
    alerts_count = db.query(Alert).count()
    users_count = db.query(User).count()

    models_loaded = {
        k: (v is not None) for k, v in inference_engine.models.items()
    }

    return {
        "status": "HEALTHY",
        "environment": "DEMO / SYNTHETIC ENVIRONMENT",
        "active_database": "SQLite (Local Zero-Config)" if "sqlite" in settings.DATABASE_URL else "PostgreSQL/PostGIS",
        "counts": {
            "wells": wells_count,
            "historical_events": events_count,
            "ingested_documents": docs_count,
            "active_alerts": alerts_count,
            "users": users_count
        },
        "ml_models": {
            "status": "ACTIVE",
            "models_loaded": models_loaded,
            "fallback_mode": not all(models_loaded.values())
        },
        "realtime_simulator": {
            "status": "STREAMING",
            "tick_interval_s": settings.SIMULATOR_TICK_SECONDS,
            "active_well_id": settings.ACTIVE_WELL_ID
        },
        "ai_assistant": {
            "status": "READY",
            "grounding": "STRICT_HISTORICAL_DATABASE_ONLY"
        }
    }

# Realtime Telemetry WebSocket Endpoints (supports both /ws/telemetry/{well_id} and legacy /ws/well/{well_id})
@app.websocket("/ws/well/{well_id}")
@app.websocket("/ws/telemetry/{well_id}")
async def websocket_well_endpoint(websocket: WebSocket, well_id: str):
    await ws_manager.connect(websocket, well_id)
    try:
        while True:
            # Keep connection open and accept client messages if any
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, well_id)
    except Exception:
        ws_manager.disconnect(websocket, well_id)
