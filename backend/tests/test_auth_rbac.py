"""
Comprehensive RBAC and Authentication Verification Matrix — Phase 1.

Tests:
1. 401 Unauthorized for missing, malformed, or invalid tokens.
2. 403 Forbidden when a user role has insufficient permissions for a route.
3. 200 OK when authorized roles access permitted endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token
from backend.app.models.alert import Alert
from backend.app.core.database import SessionLocal

client = TestClient(app)


# ── 1. Unauthenticated Checks (HTTP 401) ──────────────────────────────────────

def test_missing_token_returns_401():
    """Any protected route without Authorization header must return 401."""
    routes = [
        ("GET", "/api/wells"),
        ("GET", "/api/formations"),
        ("GET", "/api/events"),
        ("GET", "/api/documents"),
        ("GET", "/api/alerts"),
        ("GET", "/api/analytics/knowledge-graph"),
        ("POST", "/api/risk/predict"),
        ("POST", "/api/search/keyword"),
    ]
    for method, path in routes:
        if method == "GET":
            res = client.get(path)
        else:
            res = client.post(path, json={})
        assert res.status_code == 401, f"{method} {path} returned {res.status_code}, expected 401"


def test_invalid_token_returns_401():
    """Malformed or invalid signature token must return 401."""
    res = client.get("/api/wells", headers={"Authorization": "Bearer invalid_garbage_token_123"})
    assert res.status_code == 401


def test_nonexistent_user_token_returns_401():
    """Token with non-existent username must return 401."""
    fake_token = create_access_token({"sub": "ghost_user_999", "role": "Viewer", "user_id": 9999})
    res = client.get("/api/wells", headers={"Authorization": f"Bearer {fake_token}"})
    assert res.status_code == 401


# ── 2. Forbidden RBAC Matrix (HTTP 403) ───────────────────────────────────────

def test_viewer_cannot_predict_risk(viewer_headers):
    """Viewer role must receive 403 on POST /risk/predict."""
    payload = {
        "well_id": "WELL-001",
        "depth": 3420.0,
        "formation_name": "Barail Sandstone",
        "rop": 5.5, "wob": 16.0, "rpm": 105.0, "torque": 18.5,
        "standpipe_pressure": 2180.0, "flow_rate": 1750.0,
        "mud_weight": 1.28, "ecd": 1.33, "hook_load": 125.0
    }
    res = client.post("/api/risk/predict", json=payload, headers=viewer_headers)
    assert res.status_code == 403
    assert "Insufficient permissions" in res.json()["detail"]


def test_viewer_cannot_search(viewer_headers):
    """Viewer role must receive 403 on POST /search/keyword."""
    res = client.post("/api/search/keyword", json={"query": "kick"}, headers=viewer_headers)
    assert res.status_code == 403


def test_viewer_cannot_acknowledge_alert(viewer_headers):
    """Viewer role must receive 403 on POST /alerts/{id}/acknowledge."""
    res = client.post(
        "/api/alerts/ALT-0001/acknowledge",
        json={"acknowledged_by": "viewer"},
        headers=viewer_headers
    )
    assert res.status_code == 403


def test_geologist_cannot_predict_risk(geologist_headers):
    """Geologist role must receive 403 on POST /risk/predict (requires Drilling Engineer)."""
    payload = {
        "well_id": "WELL-001",
        "depth": 3420.0,
        "formation_name": "Barail Sandstone",
        "rop": 5.5, "wob": 16.0, "rpm": 105.0, "torque": 18.5,
        "standpipe_pressure": 2180.0, "flow_rate": 1750.0,
        "mud_weight": 1.28, "ecd": 1.33, "hook_load": 125.0
    }
    res = client.post("/api/risk/predict", json=payload, headers=geologist_headers)
    assert res.status_code == 403


def test_geologist_cannot_acknowledge_alert(geologist_headers):
    """Geologist role must receive 403 on POST /alerts/{id}/acknowledge (requires Supervisor)."""
    res = client.post(
        "/api/alerts/ALT-0001/acknowledge",
        json={"acknowledged_by": "geologist"},
        headers=geologist_headers
    )
    assert res.status_code == 403


def test_supervisor_cannot_predict_risk(supervisor_headers):
    """Supervisor role must receive 403 on POST /risk/predict (requires Drilling Engineer)."""
    payload = {
        "well_id": "WELL-001",
        "depth": 3420.0,
        "formation_name": "Barail Sandstone",
        "rop": 5.5, "wob": 16.0, "rpm": 105.0, "torque": 18.5,
        "standpipe_pressure": 2180.0, "flow_rate": 1750.0,
        "mud_weight": 1.28, "ecd": 1.33, "hook_load": 125.0
    }
    res = client.post("/api/risk/predict", json=payload, headers=supervisor_headers)
    assert res.status_code == 403


# ── 3. Authorized Operations Matrix (HTTP 200) ────────────────────────────────

def test_viewer_can_read_wells_and_formations(viewer_headers):
    """Viewer role is authorized to perform all GET queries."""
    res = client.get("/api/wells", headers=viewer_headers)
    assert res.status_code == 200

    res_fmt = client.get("/api/formations", headers=viewer_headers)
    assert res_fmt.status_code == 200


def test_geologist_can_search(geologist_headers):
    """Geologist role is authorized for search endpoints."""
    res = client.post("/api/search/keyword", json={"query": "shale"}, headers=geologist_headers)
    assert res.status_code == 200


def test_supervisor_can_acknowledge_alert(supervisor_headers):
    """Supervisor role is authorized to acknowledge alerts."""
    db = SessionLocal()
    alert = db.query(Alert).first()
    db.close()
    if alert:
        res = client.post(
            f"/api/alerts/{alert.alert_id}/acknowledge",
            json={"acknowledged_by": "Debabrata Sarmah"},
            headers=supervisor_headers
        )
        assert res.status_code == 200
        assert res.json()["status"] == "ACKNOWLEDGED"


def test_driller_can_predict_risk(driller_headers):
    """Drilling Engineer role is authorized to run risk predictions."""
    payload = {
        "well_id": "WELL-001",
        "depth": 3420.0,
        "formation_name": "Barail Sandstone",
        "rop": 5.5, "wob": 16.0, "rpm": 105.0, "torque": 18.5,
        "standpipe_pressure": 2180.0, "flow_rate": 1750.0,
        "mud_weight": 1.28, "ecd": 1.33, "hook_load": 125.0
    }
    res = client.post("/api/risk/predict", json=payload, headers=driller_headers)
    assert res.status_code == 200
    assert "predictions" in res.json()
    assert "overall_risk_level" in res.json()


def test_admin_can_perform_all_operations(admin_headers):
    """Admin has full access across all operations."""
    res_get = client.get("/api/wells", headers=admin_headers)
    assert res_get.status_code == 200

    payload = {
        "well_id": "WELL-001",
        "depth": 3420.0,
        "formation_name": "Barail Sandstone",
        "rop": 5.5, "wob": 16.0, "rpm": 105.0, "torque": 18.5,
        "standpipe_pressure": 2180.0, "flow_rate": 1750.0,
        "mud_weight": 1.28, "ecd": 1.33, "hook_load": 125.0
    }
    res_post = client.post("/api/risk/predict", json=payload, headers=admin_headers)
    assert res_post.status_code == 200
