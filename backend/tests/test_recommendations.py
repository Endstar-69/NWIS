"""
Unit and Integration Tests for Phase 8 — Dynamic Evidence-Based Recommendations.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.recommendation_service import (
    generate_dynamic_recommendation, get_recommendations_for_well, get_active_well_formation
)
from backend.app.schemas.alert import RecommendationSchema
from backend.app.core.database import SessionLocal

client = TestClient(app)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_stratigraphic_formation_lookup(db_session):
    fmt_3400 = get_active_well_formation(db_session, "WELL-001", 3420.0)
    assert "Barail" in fmt_3400 or "Sandstone" in fmt_3400

    fmt_1900 = get_active_well_formation(db_session, "WELL-001", 1900.0)
    assert len(fmt_1900) > 0


def test_dynamic_recommendation_mud_loss(db_session):
    rec = generate_dynamic_recommendation(
        db=db_session,
        well_id="WELL-001",
        depth=3420.0,
        formation="Barail Sandstone",
        active_hazard="MUD_LOSS"
    )

    assert isinstance(rec, RecommendationSchema)
    assert rec.well_id == "WELL-001"
    assert rec.depth == 3420.0
    assert rec.dominant_hazard == "MUD_LOSS"

    # Title must be dynamically generated, not a static string
    assert "Lost Circulation" in rec.title or "Seepage" in rec.title or "MUD_LOSS" in rec.title
    assert "Barail" in rec.title
    assert "3420" in rec.title

    # Summary must reference active well and empirical evidence
    assert "Barail Sandstone" in rec.summary
    assert len(rec.action_steps) >= 2
    assert len(rec.evidence_sources) > 0

    # Verify evidence source fields
    top_src = rec.evidence_sources[0]
    assert "well_name" in top_src
    assert "source_document" in top_src
    assert "mitigation" in top_src

    # Calibrated confidence
    assert 0.60 <= rec.confidence <= 0.95


def test_dynamic_recommendation_stuck_pipe(db_session):
    rec = generate_dynamic_recommendation(
        db=db_session,
        well_id="WELL-002",
        depth=2850.0,
        formation="Kopili Shale",
        active_hazard="STUCK_PIPE"
    )

    assert rec.dominant_hazard == "STUCK_PIPE"
    assert "Sticking" in rec.title or "Pack-off" in rec.title or "STUCK_PIPE" in rec.title
    assert "Kopili" in rec.title
    assert len(rec.action_steps) > 0
    assert any("rotation" in s.lower() or "overpull" in s.lower() or "action" in s.lower() for s in rec.action_steps)


def test_dynamic_recommendation_kick(db_session):
    rec = generate_dynamic_recommendation(
        db=db_session,
        well_id="WELL-003",
        depth=3100.0,
        formation="Tipam Sandstone",
        active_hazard="KICK"
    )

    assert rec.dominant_hazard == "KICK"
    assert "Kick" in rec.title or "Influx" in rec.title
    assert "Tipam" in rec.title
    assert len(rec.precautions) > 0


def test_get_recommendations_endpoint(viewer_headers):
    # Authenticated user can read recommendations for well
    resp = client.get("/api/recommendations/WELL-001", headers=viewer_headers)
    assert resp.status_code == 200
    recs = resp.json()
    assert isinstance(recs, list)
    assert len(recs) >= 1

    top = recs[0]
    assert "title" in top
    assert "action_steps" in top
    assert "historical_evidence" in top
    assert len(top["action_steps"]) > 0


def test_get_recommendations_with_force_refresh(driller_headers):
    # Driller can force refresh recommendations for specific depth and hazard
    resp = client.get(
        "/api/recommendations/WELL-001?depth=2400.0&hazard=STUCK_PIPE&force_refresh=true",
        headers=driller_headers
    )
    assert resp.status_code == 200
    recs = resp.json()
    assert len(recs) >= 1
    assert recs[0]["depth"] == 2400.0
    assert recs[0]["dominant_hazard"] == "STUCK_PIPE"


def test_post_generate_recommendation_endpoint(driller_headers):
    payload = {
        "well_id": "WELL-001",
        "depth": 3350.0,
        "formation": "Barail Sandstone",
        "active_hazard": "MUD_LOSS"
    }
    resp = client.post("/api/recommendations/generate", json=payload, headers=driller_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["well_id"] == "WELL-001"
    assert data["depth"] == 3350.0
    assert data["dominant_hazard"] == "MUD_LOSS"
    assert len(data["evidence_sources"]) > 0


def test_recommendations_unauthenticated_returns_401():
    resp = client.get("/api/recommendations/WELL-001")
    assert resp.status_code == 401
